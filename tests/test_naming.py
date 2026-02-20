# Copyright 2026 David Eliasson
# Licensed under the Apache License, Version 2.0

"""Tests för naming.py"""

import pytest

from sv_rattspraxis.naming import (
    MalnummerParser,
    generate_filename,
    parse_referat_nummer,
    validate_filename,
)


class TestMalnummerParser:
    """Tests för målnummerparsning."""

    def test_parse_single_basic(self):
        """Grundläggande målnummer."""
        assert MalnummerParser.parse_single("4033-09") == "4033-09"

    def test_parse_single_with_prefix(self):
        """Målnummer med prefix - implementationen extraherar bara numret."""
        result = MalnummerParser.parse_single("M 4256-10")
        # Implementationen extraherar 4256-10 utan prefix
        assert result == "4256-10"

    def test_normalize_interval_chars(self):
        """Normalisera intervalltecken."""
        assert MalnummerParser.normalize_interval_chars("6107–6109-23") == "6107--6109-23"

    def test_split_list_comma(self):
        """Komma-separerad lista."""
        result = MalnummerParser.split_list("6963-15, 6969-15")
        assert result == ["6963-15", "6969-15"]

    def test_split_list_och(self):
        """Lista med 'och'."""
        result = MalnummerParser.split_list("6980-24 och 6981-24")
        assert result == ["6980-24", "6981-24"]

    def test_split_list_samt(self):
        """Lista med 'samt'."""
        result = MalnummerParser.split_list("6980-24 samt 6981-24")
        assert result == ["6980-24", "6981-24"]

    def test_parse_range_endash(self):
        """Intervall med en-dash."""
        result = MalnummerParser.parse_range("6107–6109-23")
        assert result == (6107, 6109, "23")

    def test_expand_range(self):
        """Expandera intervall."""
        result = MalnummerParser.expand_range(6107, 6109, "23")
        assert result == ["6107-23", "6108-23", "6109-23"]

    def test_parse_malnummer_lista_single(self):
        """Enkelt målnummer."""
        all_mal, primary = MalnummerParser.parse_malnummer_lista(["4033-09"])
        assert all_mal == ["4033-09"]
        assert primary == "4033-09"

    def test_parse_malnummer_lista_multiple(self):
        """Flera målnummer."""
        all_mal, primary = MalnummerParser.parse_malnummer_lista(["6963-15", "6969-15"])
        assert len(all_mal) == 2
        assert primary == "6963-15"

    def test_parse_malnummer_lista_range(self):
        """Intervall av målnummer."""
        all_mal, primary = MalnummerParser.parse_malnummer_lista(["6107–6109-23"])
        assert all_mal == ["6107-23", "6108-23", "6109-23"]
        assert primary == "6107-23"

    def test_parse_malnummer_lista_mixed(self):
        """Blandat: intervall + enskilda."""
        all_mal, primary = MalnummerParser.parse_malnummer_lista(
            ["6107–6109-23 och 6200-23"]
        )
        assert "6107-23" in all_mal
        assert "6109-23" in all_mal
        assert "6200-23" in all_mal

    def test_parse_malnummer_lista_empty(self):
        """Tom lista."""
        all_mal, primary = MalnummerParser.parse_malnummer_lista([])
        assert all_mal == []
        assert primary == "UNKNOWN"


class TestFilenameGeneration:
    """Tests för filnamnsgenerering."""

    def test_generate_filename_json(self):
        """JSON-filnamn med ny signatur."""
        filename = generate_filename("HFD", 2011, 1, "4033-09", "json")
        assert filename == "HFD_2011_ref-001__mal-4033-09.json"

    def test_generate_filename_pdf(self):
        """PDF-filnamn med ny signatur."""
        filename = generate_filename("HDO", 2025, 59, "7343-24", "pdf")
        assert filename == "HDO_2025_ref-059__mal-7343-24.pdf"

    def test_generate_filename_padding(self):
        """3-siffrig nollutfyllning."""
        filename = generate_filename("HFD", 2020, 5, "1234-20", "json")
        assert filename == "HFD_2020_ref-005__mal-1234-20.json"

    def test_validate_filename_valid(self):
        """Giltigt filnamn."""
        assert validate_filename("HFD_2011_ref-001__mal-4033-09.json") is True
        assert validate_filename("HDO_2025_ref-059__mal-T1234-24.pdf") is True

    def test_validate_filename_invalid(self):
        """Ogiltigt filnamn."""
        assert validate_filename("invalid.json") is False
        assert validate_filename("HFD_2011_ref-1__mal-4033-09.json") is False


class TestReferatnummerParsning:
    """Tests för referatnummerparsning."""

    def test_parse_referat_nummer_hfd(self):
        """HFD-format."""
        year, ref_no = parse_referat_nummer("HFD 2011 ref. 1")
        assert year == 2011
        assert ref_no == 1

    def test_parse_referat_nummer_hfd_high_number(self):
        """HFD högt nummer."""
        year, ref_no = parse_referat_nummer("HFD 2022 ref. 45")
        assert year == 2022
        assert ref_no == 45

    def test_parse_referat_nummer_ra(self):
        """RÅ-format."""
        year, ref_no = parse_referat_nummer("RÅ 2010 ref. 8")
        assert year == 2010
        assert ref_no == 8

    def test_parse_referat_nummer_invalid(self):
        """Ogiltigt format (fallback)."""
        year, ref_no = parse_referat_nummer("HFD 2023 45")
        assert year == 2023
        assert ref_no == 45

    def test_parse_referat_nummer_missing_ref(self):
        """Format utan 'ref.' (fallback)."""
        year, ref_no = parse_referat_nummer("HFD 2023 nr 10")
        assert year == 2023
        assert ref_no == 10
