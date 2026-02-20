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
Verifiering och integritetskontroll av hämtad data.

Kontrollerar:
- Sekvenskontinuitet (ref 1→N per år)
- SHA-256 checksums
- Duplikatkontroll
- Flaggar luckor i sekvensen
"""

from collections import defaultdict
from pathlib import Path

import structlog

from .models import MasterListEntry

logger = structlog.get_logger()


class VerificationReport:
    """Rapport från verifiering."""

    def __init__(self):
        self.total_entries = 0
        self.years_covered: set[int] = set()
        self.sequence_gaps: list[tuple[int, int, int]] = []  # (year, missing_ref_no, gap_size)
        self.duplicates: list[str] = []  # [referat_nummer, ...]
        self.checksum_failures: list[str] = []  # [filnamn, ...]
        self.missing_files: list[str] = []  # [filnamn, ...]

    def is_valid(self) -> bool:
        """
        Returnerar True om inga kritiska fel.

        Kritiska fel:
        - Saknade filer
        - Checksum-fel
        - Dubbletter

        Icke-kritiska varningar:
        - Sekvensavbrott (kan vara korrekt om vissa ref inte publicerats)
        """
        return (
            len(self.missing_files) == 0
            and len(self.checksum_failures) == 0
            and len(self.duplicates) == 0
        )

    def print_report(self):
        """Skriver ut rapport till stderr (via structlog)."""
        logger.info(
            "verification_summary",
            total_entries=self.total_entries,
            years_covered=sorted(self.years_covered),
            sequence_gaps=len(self.sequence_gaps),
            duplicates=len(self.duplicates),
            checksum_failures=len(self.checksum_failures),
            missing_files=len(self.missing_files),
            valid=self.is_valid(),
        )

        if self.sequence_gaps:
            logger.warning(
                "sequence_gaps_found",
                gaps=self.sequence_gaps[:10],  # Visa max 10
                total_gaps=len(self.sequence_gaps),
            )

        if self.duplicates:
            logger.error(
                "duplicates_found",
                duplicates=self.duplicates[:10],
                total_duplicates=len(self.duplicates),
            )

        if self.checksum_failures:
            logger.error(
                "checksum_failures",
                files=self.checksum_failures[:10],
                total_failures=len(self.checksum_failures),
            )

        if self.missing_files:
            logger.error(
                "missing_files",
                files=self.missing_files[:10],
                total_missing=len(self.missing_files),
            )

        if self.is_valid():
            logger.info("verification_passed", status="✅ Verifiering OK")
        else:
            logger.error("verification_failed", status="❌ Verifiering misslyckades")


class Verifier:
    """
    Verifiering av hämtad data.

    Läser masterlist.csv och kontrollerar:
    1. Sekvenskontinuitet per år
    2. Att alla filer existerar
    3. SHA-256 checksums
    4. Inga dubbletter
    """

    def __init__(self, data_root: Path):
        """
        Initierar verifier.

        Args:
            data_root: Rot för data/ (förväntar processed/ och raw/ under denna)
        """
        self.data_root = Path(data_root)
        self.masterlist_path = self.data_root / "processed" / "masterlist.csv"
        self.raw_dir = self.data_root / "raw"

        logger.info(
            "verifier_initialized",
            data_root=str(data_root),
            masterlist_exists=self.masterlist_path.exists(),
        )

    def load_masterlist(self) -> list[MasterListEntry]:
        """
        Läser masterlist.csv.

        Returns:
            Lista av MasterListEntry

        Raises:
            FileNotFoundError: Om masterlist.csv saknas
        """
        if not self.masterlist_path.exists():
            raise FileNotFoundError(f"Masterlist saknas: {self.masterlist_path}")

        lines = self.masterlist_path.read_text(encoding="utf-8").strip().split("\n")

        # Skippa header
        entries = []
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 12:
                logger.warning("masterlist_invalid_line", line=line)
                continue

            entry = MasterListEntry(
                api_id=parts[0],
                domstol=parts[1],
                typ=parts[2],
                referat_nummer=parts[3],
                year=int(parts[4]),
                ref_no=int(parts[5]),
                ref_no_padded=parts[6],
                malnummer_primart=parts[7],
                avgorandedatum=parts[8],
                filnamn_json=parts[9],
                sha256_json=parts[10],
                harvest_timestamp=parts[11],
            )
            entries.append(entry)

        logger.info("masterlist_loaded", entries=len(entries))
        return entries

    def verify_sequence(self, entries: list[MasterListEntry]) -> list[tuple[int, int, int]]:
        """
        Verifierar sekvenskontinuitet per år.

        Args:
            entries: Lista av MasterListEntry

        Returns:
            Lista av gaps: [(year, missing_ref_no, gap_size), ...]

        Example:
            Om 2011 har ref 1, 2, 4, 5 → gap vid ref 3, gap_size=1
        """
        # Gruppera per år
        by_year: dict[int, list[int]] = defaultdict(list)
        for entry in entries:
            by_year[entry.year].append(entry.ref_no)

        gaps = []

        for year, ref_nos in sorted(by_year.items()):
            ref_nos_sorted = sorted(ref_nos)
            expected_sequence = list(range(1, max(ref_nos_sorted) + 1))

            missing = set(expected_sequence) - set(ref_nos_sorted)

            if missing:
                for missing_ref in sorted(missing):
                    gaps.append((year, missing_ref, 1))
                    logger.warning(
                        "sequence_gap",
                        year=year,
                        missing_ref=missing_ref,
                    )

        return gaps

    def verify_checksums(self, entries: list[MasterListEntry]) -> list[str]:
        """
        Verifierar SHA-256 checksums.

        Args:
            entries: Lista av MasterListEntry

        Returns:
            Lista av filnamn där checksum inte matchar
        """
        from .harvester import Harvester

        failures = []

        for entry in entries:
            filepath = self.raw_dir / entry.filnamn_json

            if not filepath.exists():
                # Hanteras i verify_files
                continue

            content = filepath.read_text(encoding="utf-8")
            computed_sha = Harvester.compute_sha256(content)

            if computed_sha != entry.sha256_json:
                failures.append(entry.filnamn_json)
                logger.error(
                    "checksum_mismatch",
                    filename=entry.filnamn_json,
                    expected=entry.sha256_json[:16] + "...",
                    computed=computed_sha[:16] + "...",
                )

        return failures

    def verify_files(self, entries: list[MasterListEntry]) -> list[str]:
        """
        Verifierar att alla filer existerar.

        Args:
            entries: Lista av MasterListEntry

        Returns:
            Lista av saknade filnamn
        """
        missing = []

        for entry in entries:
            filepath = self.raw_dir / entry.filnamn_json

            if not filepath.exists():
                missing.append(entry.filnamn_json)
                logger.error(
                    "file_missing",
                    filename=entry.filnamn_json,
                    referat_nummer=entry.referat_nummer,
                )

        return missing

    def verify_duplicates(self, entries: list[MasterListEntry]) -> list[str]:
        """
        Verifierar att inga dubbletter finns.

        Args:
            entries: Lista av MasterListEntry

        Returns:
            Lista av referatnummer som förekommer flera gånger
        """
        seen: dict[str, int] = {}
        duplicates = []

        for entry in entries:
            key = entry.referat_nummer
            if key in seen:
                duplicates.append(key)
                logger.error(
                    "duplicate_found",
                    referat_nummer=key,
                    occurrences=seen[key] + 1,
                )
            else:
                seen[key] = 1

        return duplicates

    def verify_all(self) -> VerificationReport:
        """
        Kör fullständig verifiering.

        Returns:
            VerificationReport med resultat
        """
        logger.info("verification_start")

        report = VerificationReport()

        # Läs masterlist
        entries = self.load_masterlist()
        report.total_entries = len(entries)
        report.years_covered = {e.year for e in entries}

        # Sekvenskontroll
        report.sequence_gaps = self.verify_sequence(entries)

        # Duplikatkontroll
        report.duplicates = self.verify_duplicates(entries)

        # Filkontroll
        report.missing_files = self.verify_files(entries)

        # Checksum-kontroll
        report.checksum_failures = self.verify_checksums(entries)

        logger.info("verification_complete")
        report.print_report()

        return report
