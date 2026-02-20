# Copyright 2026 David Eliasson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Harvester för systematisk inhämtning av HFD-referat.

Hanterar:
- Paginerad inhämtning (12 sidor × 100 = 1 117 referat)
- Lagring av rå JSON
- Generering av masterlist
- SHA-256 checksums
"""

import hashlib
from datetime import datetime
from pathlib import Path

import structlog

from .api_client import APIClient
from .models import MasterListEntry, Publication, SearchFilter, SearchRequest
from .naming import MalnummerParser, generate_filename, parse_referat_nummer

logger = structlog.get_logger()

HARVESTER_VERSION = "1.0.0"


class Harvester:
    """
    Systematisk inhämtning av HFD-avgöranden.

    Sparar:
    - data/raw/{filnamn}.json — rå API-svar per publikation
    - data/processed/masterlist.csv — index över alla referat
    """

    def __init__(
        self,
        data_root: Path,
        api_client: APIClient,
        from_year: int = 2011,
        to_year: int | None = None,
        typ: str = "REFERAT",
    ):
        """
        Initierar harvester.

        Args:
            data_root: Rot för data/ (skapar raw/, processed/ under denna)
            api_client: Initialiserad APIClient
            from_year: Starta från detta år (inkluderat)
            to_year: Sluta vid detta år (inkluderat), None = nuvarande år
            typ: REFERAT eller NOTIS
        """
        self.data_root = Path(data_root)
        self.api_client = api_client
        self.from_year = from_year
        self.to_year = to_year or datetime.now().year
        self.typ = typ

        # Skapa kataloger
        self.raw_dir = self.data_root / "raw"
        self.processed_dir = self.data_root / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "harvester_initialized",
            data_root=str(data_root),
            from_year=from_year,
            to_year=self.to_year,
            typ=typ,
        )

    @staticmethod
    def compute_sha256(content: str) -> str:
        """
        Beräknar SHA-256 hash av innehåll.

        Args:
            content: Text att hasha

        Returns:
            Hex-sträng (64 tecken)
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def save_raw_json(self, publication: Publication, filename: str) -> str:
        """
        Sparar rå JSON från API.

        Args:
            publication: Publication-objekt
            filename: Filnamn (utan .json-suffix om det redan finns)

        Returns:
            SHA-256 hash av sparad JSON

        Example:
            >>> sha = harvester.save_raw_json(pub, "HFD_2011_ref-001__mal-4033-09")
        """
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        filepath = self.raw_dir / filename

        # Serialisera till JSON med pretty-print
        json_content = publication.model_dump_json(indent=2, exclude_none=False)

        # Spara
        filepath.write_text(json_content, encoding="utf-8")

        # Beräkna hash
        sha256 = self.compute_sha256(json_content)

        logger.info(
            "raw_json_saved",
            filename=filename,
            size_bytes=len(json_content),
            sha256=sha256[:16] + "...",  # Logga endast första 16 tecken
        )

        return sha256

    async def harvest_all(self) -> list[MasterListEntry]:
        """
        Hämtar alla referat/notiser för angivet datumintervall.

        Returns:
            Lista av MasterListEntry för masterlist

        Example:
            >>> entries = await harvester.harvest_all()
            >>> print(f"Hämtade {len(entries)} referat")
        """
        from_date = f"{self.from_year}-01-01"
        to_date = f"{self.to_year}-12-31"

        logger.info(
            "harvest_start",
            from_date=from_date,
            to_date=to_date,
            typ=self.typ,
        )

        # Första sökningen för att få totalt antal
        initial_request = SearchRequest(
            antalPerSida=100,
            asc=True,  # Äldst först
            sidIndex=0,
            filter=SearchFilter(
                avgorandeTypLista=[self.typ],
                intervall={"fromDatum": from_date, "toDatum": to_date},
                domstolKodLista=["HFD"],
            ),
        )

        initial_response = await self.api_client.search(initial_request)
        total_publications = initial_response.total
        total_pages = (total_publications + 99) // 100  # Beräkna antal sidor (ceil division)

        logger.info(
            "harvest_initial_response",
            total_publications=total_publications,
            total_pages=total_pages,
        )

        # Samla alla publikationer
        all_publications: list[Publication] = []
        all_publications.extend(initial_response.publiceringLista)

        # Hämta resterande sidor
        for page_index in range(1, total_pages):
            logger.info(
                "harvest_page",
                page_index=page_index,
                total_pages=total_pages,
                progress=f"{page_index}/{total_pages}",
            )

            request = SearchRequest(
                antalPerSida=100,
                asc=True,
                sidIndex=page_index,
                filter=initial_request.filter,
            )

            response = await self.api_client.search(request)
            all_publications.extend(response.publiceringLista)

        logger.info(
            "harvest_complete",
            total_fetched=len(all_publications),
            expected=total_publications,
            match=len(all_publications) == total_publications,
        )

        # Bearbeta och spara
        masterlist_entries = []

        for pub in all_publications:
            entry = self.process_publication(pub)
            if entry:
                masterlist_entries.append(entry)

        # Spara masterlist
        self.save_masterlist(masterlist_entries)

        return masterlist_entries

    def process_publication(self, pub: Publication) -> MasterListEntry | None:
        """
        Bearbetar en publikation och sparar till disk.

        Args:
            pub: Publication-objekt från API

        Returns:
            MasterListEntry om framgång, None vid fel
        """
        try:
            # Extrahera referatnummer
            if not pub.referatNummerLista:
                logger.warning(
                    "publication_missing_referat_nummer",
                    api_id=str(pub.id),
                )
                return None

            referat_nummer = pub.referatNummerLista[0]
            year, ref_no = parse_referat_nummer(referat_nummer)

            # Parsa målnummer
            alla_malnummer, malnummer_primart = MalnummerParser.parse_malnummer_lista(
                pub.malNummerLista
            )

            # Generera filnamn
            filename = generate_filename(year, ref_no, malnummer_primart, "json")

            # Spara rå JSON
            sha256 = self.save_raw_json(pub, filename)

            # Skapa masterlist-entry
            entry = MasterListEntry(
                api_id=pub.id,
                domstol=pub.domstol.domstolKod,
                typ=pub.typ,
                referat_nummer=referat_nummer,
                year=year,
                ref_no=ref_no,
                ref_no_padded=f"{ref_no:03d}",
                malnummer_primart=malnummer_primart,
                avgorandedatum=pub.avgorandedatum,
                filnamn_json=filename,
                sha256_json=sha256,
                harvest_timestamp=datetime.now().isoformat(),
            )

            logger.info(
                "publication_processed",
                referat_nummer=referat_nummer,
                filename=filename,
                malnummer_antal=len(alla_malnummer),
            )

            return entry

        except Exception as e:
            logger.error(
                "publication_processing_failed",
                api_id=str(pub.id),
                error=str(e),
                exc_info=True,
            )
            return None

    def save_masterlist(self, entries: list[MasterListEntry]) -> Path:
        """
        Sparar masterlist.csv.

        Args:
            entries: Lista av MasterListEntry

        Returns:
            Path till sparad fil

        Example:
            >>> path = harvester.save_masterlist(entries)
            >>> print(f"Masterlist sparad: {path}")
        """
        filepath = self.processed_dir / "masterlist.csv"

        # Sortera efter år och refnr
        entries_sorted = sorted(entries, key=lambda e: (e.year, e.ref_no))

        # CSV-header
        header = [
            "api_id",
            "domstol",
            "typ",
            "referat_nummer",
            "year",
            "ref_no",
            "ref_no_padded",
            "malnummer_primart",
            "avgorandedatum",
            "filnamn_json",
            "sha256_json",
            "harvest_timestamp",
        ]

        lines = [",".join(header)]

        for entry in entries_sorted:
            row = [
                str(entry.api_id),
                entry.domstol,
                entry.typ,
                entry.referat_nummer,
                str(entry.year),
                str(entry.ref_no),
                entry.ref_no_padded,
                entry.malnummer_primart,
                entry.avgorandedatum,
                entry.filnamn_json,
                entry.sha256_json,
                entry.harvest_timestamp,
            ]
            lines.append(",".join(row))

        csv_content = "\n".join(lines)
        filepath.write_text(csv_content, encoding="utf-8")

        logger.info(
            "masterlist_saved",
            filepath=str(filepath),
            antal_entries=len(entries_sorted),
            size_bytes=len(csv_content),
        )

        return filepath
