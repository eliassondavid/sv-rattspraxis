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
Filnamnskonvention för HFD-referat.

Implementerar LÅST konvention från projektspecifikationen:
HFD_{YEAR}_ref-{NNN}__mal-{MALNR}.json

Hanterar:
- Målnummer i olika format (se HFD-mal_nr.md)
- Interval-målnummer (normalisering till första numret)
- Flera enskilda målnummer (använd det först listade)
"""

import re

import structlog

logger = structlog.get_logger()


class MalnummerParser:
    """
    Parsar och normaliserar HFD-målnummer.

    Hanterar alla varianter enligt HFD-mal_nr.md:
    - Grundformat: 1536-23
    - Listor: 6963-15, 6969-15
    - Intervall: 6107–6109-23, 6159--6160-14
    - Kombinationer: 6578-14, 6159--6160-14
    """

    # Regex för enskilt målnummer: NNNN-NN
    SINGLE_PATTERN = re.compile(r"(?<!\d)(\d{1,5}-\d{2})(?!\d)")

    # Regex för intervall: NNNN[-–--]NNNN-NN
    RANGE_PATTERN = re.compile(r"(?<!\d)(\d{1,5})(?:--|–|-)(\d{1,5})-(\d{2})(?!\d)")

    @classmethod
    def normalize_interval_chars(cls, text: str) -> str:
        """
        Normaliserar intervalltecken till dubbelt bindestreck (--).

        Args:
            text: Råtext med målnummer

        Returns:
            Text där – (en-dash) ersatts med --
        """
        # En-dash → dubbelt bindestreck
        return text.replace("–", "--")

    @classmethod
    def split_list(cls, text: str) -> list[str]:
        """
        Delar upp lista av målnummer.

        Splittar på:
        - Komma
        - " och "
        - " samt "

        Args:
            text: Råtext med målnummer

        Returns:
            Lista av tokens
        """
        # Ta bort prefix som "Mål:", "mål nr", "Mål nr."
        text = re.sub(r"(Mål|mål)\s*(nr\.?|:)\s*", "", text, flags=re.IGNORECASE)

        # Splitta på komma och konjunktioner
        text = text.replace(" och ", ",").replace(" samt ", ",")
        tokens = [t.strip() for t in text.split(",") if t.strip()]

        return tokens

    @classmethod
    def parse_single(cls, token: str) -> str | None:
        """
        Parsar enskilt målnummer.

        Args:
            token: Token som kan vara ett målnummer

        Returns:
            Målnummer om matchning, annars None
        """
        match = cls.SINGLE_PATTERN.search(token)
        return match.group(1) if match else None

    @classmethod
    def parse_range(cls, token: str) -> tuple[int, int, str] | None:
        """
        Parsar intervall-målnummer.

        Args:
            token: Token som kan vara ett intervall

        Returns:
            (start, slut, år) om matchning, annars None

        Example:
            >>> MalnummerParser.parse_range("6107--6109-23")
            (6107, 6109, "23")
        """
        match = cls.RANGE_PATTERN.search(token)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            year = match.group(3)
            return (start, end, year)
        return None

    @classmethod
    def expand_range(cls, start: int, end: int, year: str) -> list[str]:
        """
        Expanderar intervall till lista av målnummer.

        Args:
            start: Startnummer
            end: Slutnummer
            year: Årssuffix (2 siffror)

        Returns:
            Lista av målnummer

        Example:
            >>> MalnummerParser.expand_range(6107, 6109, "23")
            ["6107-23", "6108-23", "6109-23"]
        """
        return [f"{n}-{year}" for n in range(start, end + 1)]

    @classmethod
    def parse_malnummer_lista(cls, raw_lista: list[str]) -> tuple[list[str], str]:
        """
        Parsar lista av målnummer från API.

        Args:
            raw_lista: Rådata från API (malNummerLista)

        Returns:
            (alla_malnummer, primart_malnummer)
            - alla_malnummer: Lista av alla målnummer (intervall expanderade)
            - primart_malnummer: Första målnumret (för filnamn)

        Example:
            >>> MalnummerParser.parse_malnummer_lista(["6107–6109-23", "7000-23"])
            (["6107-23", "6108-23", "6109-23", "7000-23"], "6107-23")
        """
        if not raw_lista:
            logger.warning("parse_malnummer_lista: tom lista")
            return ([], "UNKNOWN")

        alla_malnummer = []
        original_form = raw_lista[0]  # För loggning

        for raw in raw_lista:
            # Normalisera intervalltecken
            normalized = cls.normalize_interval_chars(raw)

            # Splitta lista (om flera målnummer i samma sträng)
            tokens = cls.split_list(normalized)

            for token in tokens:
                # Testa intervall först
                range_match = cls.parse_range(token)
                if range_match:
                    start, end, year = range_match
                    expanded = cls.expand_range(start, end, year)
                    alla_malnummer.extend(expanded)
                    logger.debug(
                        "parse_malnummer_range",
                        original=raw,
                        token=token,
                        expanded=expanded,
                    )
                    continue

                # Testa enskilt målnummer
                single_match = cls.parse_single(token)
                if single_match:
                    alla_malnummer.append(single_match)
                    logger.debug(
                        "parse_malnummer_single",
                        original=raw,
                        token=token,
                        parsed=single_match,
                    )
                    continue

                # Kunde inte parsa
                logger.warning("parse_malnummer_failed", token=token, original=raw)

        # Primärt målnummer = första i listan
        primart = alla_malnummer[0] if alla_malnummer else "UNKNOWN"

        if primart == "UNKNOWN":
            logger.error(
                "parse_malnummer_no_valid",
                raw_lista=raw_lista,
                original_form=original_form,
            )

        return (alla_malnummer, primart)


def generate_filename(
    year: int,
    ref_no: int,
    malnummer_primart: str,
    extension: str = "json",
) -> str:
    """
    Genererar filnamn enligt LÅST konvention.

    Format: HFD_{YEAR}_ref-{NNN}__mal-{MALNR}.{ext}

    Args:
        year: 4-siffrigt år (2011-2025)
        ref_no: Referatnummer (1-999)
        malnummer_primart: Första målnumret (t.ex. "4033-09")
        extension: Filändelse ("json" eller "pdf")

    Returns:
        Filnamn-sträng

    Example:
        >>> generate_filename(2011, 1, "4033-09", "json")
        "HFD_2011_ref-001__mal-4033-09.json"
    """
    ref_no_padded = f"{ref_no:03d}"
    return f"HFD_{year}_ref-{ref_no_padded}__mal-{malnummer_primart}.{extension}"


def parse_referat_nummer(referat_nummer: str) -> tuple[int, int]:
    """
    Parsar referatnummer till år och löpnummer.

    Args:
        referat_nummer: T.ex. "HFD 2011 ref. 1"

    Returns:
        (year, ref_no)

    Raises:
        ValueError: Om formatet inte matchar

    Example:
        >>> parse_referat_nummer("HFD 2011 ref. 1")
        (2011, 1)
    """
    # Regex: "HFD YYYY ref. N" eller "RÅ YYYY ref. N"
    pattern = r"(HFD|RÅ)\s+(\d{4})\s+ref\.\s+(\d+)"
    match = re.search(pattern, referat_nummer)

    if not match:
        raise ValueError(f"Kunde inte parsa referatnummer: {referat_nummer}")

    year = int(match.group(2))
    ref_no = int(match.group(3))

    return (year, ref_no)


def validate_filename(filename: str) -> bool:
    """
    Validerar att filnamn följer konventionen.

    Args:
        filename: Filnamn att validera

    Returns:
        True om giltigt, annars False

    Example:
        >>> validate_filename("HFD_2011_ref-001__mal-4033-09.json")
        True
        >>> validate_filename("invalid.json")
        False
    """
    pattern = r"^HFD_\d{4}_ref-\d{3}__mal-\d{1,5}-\d{2}\.(json|pdf)$"
    return bool(re.match(pattern, filename))
