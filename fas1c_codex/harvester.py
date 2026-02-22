"""Harvester för systematisk inhämtning av avgöranden per domstol."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from .courts import COURTS, CourtConfig
from .naming import MalnummerParser, generate_filename, parse_referat_nummer

logger = structlog.get_logger()

HARVESTER_VERSION = "1.1.0"


@dataclass(slots=True)
class MasterListEntry:
    """Intern representation av en rad i masterlist."""

    api_id: str
    domstol: str
    typ: str
    referat_nummer: str
    year: int
    ref_no: int
    ref_no_padded: str
    malnummer_primart: str
    avgorandedatum: str
    filnamn_json: str
    sha256_json: str
    harvest_timestamp: str

    def as_csv_row(self) -> list[str]:
        return [
            self.api_id,
            self.domstol,
            self.typ,
            self.referat_nummer,
            str(self.year),
            str(self.ref_no),
            self.ref_no_padded,
            self.malnummer_primart,
            self.avgorandedatum,
            self.filnamn_json,
            self.sha256_json,
            self.harvest_timestamp,
        ]


class DomstolHarvester:
    """Systematisk inhämtning av avgöranden för en vald domstol."""

    def __init__(
        self,
        data_root: Path,
        api_client: Any,
        domstol_kod: str = "HFD",
        from_year: int = 2011,
        to_year: int | None = None,
        typ: str = "REFERAT",
    ) -> None:
        self.data_root = Path(data_root)
        self.api_client = api_client
        self.domstol = domstol_kod.upper()
        self.from_year = from_year
        self.to_year = to_year or datetime.now().year
        self.typ = typ.upper()

        if self.domstol not in COURTS:
            raise ValueError(f"Okänd domstol: {domstol_kod}")

        self.config: CourtConfig = COURTS[self.domstol]
        self._fallback_ref_counter: dict[int, int] = {}

        self.raw_dir = self.data_root / "raw"
        self.processed_dir = self.data_root / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "harvester_initialized",
            domstol=self.domstol,
            data_root=str(self.data_root),
            from_year=self.from_year,
            to_year=self.to_year,
            typ=self.typ,
        )

    @staticmethod
    def compute_sha256(content: str) -> str:
        """Beräknar SHA-256 hash av textinnehåll."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _get_attr(item: Any, field: str, default: Any = None) -> Any:
        if isinstance(item, dict):
            return item.get(field, default)
        return getattr(item, field, default)

    @staticmethod
    def _serialize_publication(publication: Any) -> str:
        if hasattr(publication, "model_dump_json"):
            return publication.model_dump_json(indent=2, exclude_none=False)

        if isinstance(publication, dict):
            return json.dumps(publication, ensure_ascii=False, indent=2)

        return json.dumps(
            publication,
            ensure_ascii=False,
            indent=2,
            default=lambda obj: getattr(obj, "__dict__", str(obj)),
        )

    def save_raw_json(self, publication: Any, filename: str) -> str:
        """Sparar rå JSON och returnerar SHA-256."""
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        filepath = self.raw_dir / filename
        json_content = self._serialize_publication(publication)
        filepath.write_text(json_content, encoding="utf-8")

        sha256 = self.compute_sha256(json_content)

        logger.info(
            "raw_json_saved",
            domstol=self.domstol,
            filename=filename,
            size_bytes=len(json_content),
            sha256=f"{sha256[:16]}...",
        )

        return sha256

    async def _search(self, request: dict[str, Any]) -> Any:
        if not hasattr(self.api_client, "search"):
            raise TypeError("api_client måste implementera async search(request)")
        return await self.api_client.search(request)

    def _extract_total(self, response: Any) -> int:
        total = self._get_attr(response, "total", 0)
        try:
            return int(total)
        except (TypeError, ValueError):
            return 0

    def _extract_publications(self, response: Any) -> list[Any]:
        publications = self._get_attr(response, "publiceringLista", [])
        if publications is None:
            return []
        return list(publications)

    def _fallback_referat(self, avgorandedatum: str) -> tuple[str, int, int]:
        """Skapar deterministiskt fallback-referat för poster utan referatnummer."""
        try:
            year = int(avgorandedatum[:4])
        except (TypeError, ValueError):
            year = self.from_year

        ref_no = self._fallback_ref_counter.get(year, 0) + 1
        self._fallback_ref_counter[year] = ref_no
        referat_nummer = f"{self.domstol} {year} ref. {ref_no}"
        return referat_nummer, year, ref_no

    async def harvest_all(self) -> list[MasterListEntry]:
        """Hämtar alla avgöranden för vald domstol/tidsspann/typ."""
        from_date = f"{self.from_year}-01-01"
        to_date = f"{self.to_year}-12-31"

        logger.info(
            "harvest_start",
            domstol=self.domstol,
            from_date=from_date,
            to_date=to_date,
            typ=self.typ,
        )

        initial_request = {
            "antalPerSida": 100,
            "asc": True,
            "sidIndex": 0,
            "filter": {
                "avgorandeTypLista": [self.typ],
                "intervall": {"fromDatum": from_date, "toDatum": to_date},
                "domstolKodLista": [self.domstol],
            },
        }

        initial_response = await self._search(initial_request)
        total_publications = self._extract_total(initial_response)
        total_pages = (total_publications + 99) // 100

        logger.info(
            "harvest_initial_response",
            domstol=self.domstol,
            total_publications=total_publications,
            total_pages=total_pages,
        )

        all_publications: list[Any] = []
        all_publications.extend(self._extract_publications(initial_response))

        for page_index in range(1, total_pages):
            request = {
                "antalPerSida": 100,
                "asc": True,
                "sidIndex": page_index,
                "filter": initial_request["filter"],
            }
            response = await self._search(request)
            all_publications.extend(self._extract_publications(response))

            logger.info(
                "harvest_page",
                domstol=self.domstol,
                page_index=page_index,
                total_pages=total_pages,
                fetched_so_far=len(all_publications),
            )

        logger.info(
            "harvest_complete",
            domstol=self.domstol,
            total_fetched=len(all_publications),
            expected=total_publications,
            match=len(all_publications) == total_publications,
        )

        entries: list[MasterListEntry] = []
        for publication in all_publications:
            entry = self.process_publication(publication)
            if entry is not None:
                entries.append(entry)

        self.save_masterlist(entries)
        return entries

    def process_publication(self, publication: Any) -> MasterListEntry | None:
        """Bearbetar en publikation till råfil + masterlist-entry."""
        try:
            referat_lista = self._get_attr(publication, "referatNummerLista", []) or []
            malnummer_lista = self._get_attr(publication, "malNummerLista", []) or []
            avgorandedatum = str(self._get_attr(publication, "avgorandedatum", ""))

            referat_nummer = ""
            if referat_lista:
                referat_nummer = str(referat_lista[0])

            if referat_nummer:
                try:
                    year, ref_no = parse_referat_nummer(referat_nummer)
                except ValueError:
                    logger.warning(
                        "referat_parse_failed_fallback",
                        domstol=self.domstol,
                        referat_nummer=referat_nummer,
                    )
                    referat_nummer, year, ref_no = self._fallback_referat(avgorandedatum)
            else:
                referat_nummer, year, ref_no = self._fallback_referat(avgorandedatum)

            all_malnummer, malnummer_primart = MalnummerParser.parse_malnummer_lista(
                list(malnummer_lista)
            )
            if not all_malnummer and malnummer_lista:
                malnummer_primart = str(malnummer_lista[0])

            filename = generate_filename(
                domstol=self.domstol,
                year=year,
                ref_no=ref_no,
                malnummer_primart=malnummer_primart,
                extension="json",
            )

            sha256 = self.save_raw_json(publication, filename)

            domstol_obj = self._get_attr(publication, "domstol", {})
            domstol_kod = str(self._get_attr(domstol_obj, "domstolKod", self.domstol))

            entry = MasterListEntry(
                api_id=str(self._get_attr(publication, "id", "UNKNOWN")),
                domstol=domstol_kod or self.domstol,
                typ=str(self._get_attr(publication, "typ", self.typ)),
                referat_nummer=referat_nummer,
                year=year,
                ref_no=ref_no,
                ref_no_padded=f"{ref_no:03d}",
                malnummer_primart=malnummer_primart,
                avgorandedatum=avgorandedatum,
                filnamn_json=filename,
                sha256_json=sha256,
                harvest_timestamp=datetime.now().isoformat(),
            )

            logger.info(
                "publication_processed",
                domstol=self.domstol,
                referat_nummer=referat_nummer,
                filename=filename,
                malnummer_antal=len(all_malnummer),
            )
            return entry

        except Exception as exc:  # pragma: no cover - defensiv loggning
            logger.error(
                "publication_processing_failed",
                domstol=self.domstol,
                api_id=str(self._get_attr(publication, "id", "UNKNOWN")),
                error=str(exc),
                exc_info=True,
            )
            return None

    def save_masterlist(self, entries: list[MasterListEntry]) -> Path:
        """Sparar masterlist.csv."""
        filepath = self.processed_dir / "masterlist.csv"

        entries_sorted = sorted(entries, key=lambda entry: (entry.year, entry.ref_no))

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

        with filepath.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for entry in entries_sorted:
                writer.writerow(entry.as_csv_row())

        logger.info(
            "masterlist_saved",
            domstol=self.domstol,
            filepath=str(filepath),
            antal_entries=len(entries_sorted),
        )

        return filepath


# Bakåtkompatibilitet med tidigare namn.
Harvester = DomstolHarvester
