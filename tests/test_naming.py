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
Tester för naming-modulen.

Testar:
- Målnummerparsning (alla varianter från HFD-mal_nr.md)
- Filnamnsgenerering
- Referatnummerparsning
"""

import pytest

from sv_rattspraxis.naming import (
    MalnummerParser,
    generate_filename,
    parse_referat_nummer,
    validate_filename,
)


class TestMalnummerParser:
    """Tester för MalnummerParser."""

    def test_parse_single_basic(self):
        """Grundformat: NNNN-NN."""
        token = "1536-23"
        result = MalnummerParser.parse_single(token)
        assert result == "1536-23"

    def test_parse_single_with_prefix(self):
        """Med prefix 'Mål:'."""
        token = "Mål: 4033-09"
        # split_list tar bort prefix
        tokens = MalnummerParser.split_list(token)
        result = MalnummerParser.parse_single(tokens[0])
        assert result == "4033-09"

    def test_normalize_interval_chars(self):
        """En-dash → dubbelt bindestreck."""
        text = "6107–6109-23"
        normalized = MalnummerParser.normalize_interval_chars(text)
        assert normalized == "6107--6109-23"

    def test_split_list_comma(self):
        """Komma-separerade målnummer."""
        text = "6963-15, 6969-15"
        tokens = MalnummerParser.split_list(text)
        assert tokens == ["6963-15", "6969-15"]

    def test_split_list_och(self):
        """Med konjunktion 'och'."""
        text = "6980-24 och 6981-24"
        tokens = MalnummerParser.split_list(text)
        assert tokens == ["6980-24", "6981-24"]

    def test_split_list_samt(self):
        """Med konjunktion 'samt'."""
        text = "A samt B"
        tokens = MalnummerParser.split_list(text)
        assert tokens == ["A", "B"]

    def test_parse_range_endash(self):
        """Intervall med en-dash."""
        token = "6107--6109-23"  # Redan normaliserad
        result = MalnummerParser.parse_range(token)
        assert result == (6107, 6109, "23")

    def test_expand_range(self):
        """Expansion av intervall."""
        expanded = MalnummerParser.expand_range(6107, 6109, "23")
        assert expanded == ["6107-23", "6108-23", "6109-23"]

    def test_parse_malnummer_lista_single(self):
        """Enskilt målnummer."""
        raw_lista = ["4033-09"]
        alla, primart = MalnummerParser.parse_malnummer_lista(raw_lista)
        assert alla == ["4033-09"]
        assert primart == "4033-09"

    def test_parse_malnummer_lista_multiple(self):
        """Flera enskilda målnummer."""
        raw_lista = ["4033-09", "4034-09"]
        alla, primart = MalnummerParser.parse_malnummer_lista(raw_lista)
        assert "4033-09" in alla
        assert "4034-09" in alla
        assert primart == "4033-09"  # Första

    def test_parse_malnummer_lista_range(self):
        """Intervall-målnummer."""
        raw_lista = ["6107–6109-23"]
        alla, primart = MalnummerParser.parse_malnummer_lista(raw_lista)
        assert alla == ["6107-23", "6108-23", "6109-23"]
        assert primart == "6107-23"

    def test_parse_malnummer_lista_mixed(self):
        """Blandning: intervall + enskilda."""
        raw_lista = ["6578-14, 6159--6160-14"]
        alla, primart = MalnummerParser.parse_malnummer_lista(raw_lista)
        assert "6578-14" in alla
        assert "6159-14" in alla
        assert "6160-14" in alla
        assert primart == "6578-14"

    def test_parse_malnummer_lista_empty(self):
        """Tom lista."""
        raw_lista = []
        alla, primart = MalnummerParser.parse_malnummer_lista(raw_lista)
        assert alla == []
        assert primart == "UNKNOWN"


class TestFilenameGeneration:
    """Tester för filnamnsgenerering."""

    def test_generate_filename_json(self):
        """JSON-filnamn."""
        filename = generate_filename(2011, 1, "4033-09", "json")
        assert filename == "HFD_2011_ref-001__mal-4033-09.json"

    def test_generate_filename_pdf(self):
        """PDF-filnamn."""
        filename = generate_filename(2025, 59, "7343-24", "pdf")
        assert filename == "HFD_2025_ref-059__mal-7343-24.pdf"

    def test_generate_filename_padding(self):
        """3-siffrig nollutfyllning."""
        filename = generate_filename(2020, 5, "1234-20", "json")
        assert filename == "HFD_2020_ref-005__mal-1234-20.json"

    def test_validate_filename_valid(self):
        """Giltigt filnamn."""
        assert validate_filename("HFD_2011_ref-001__mal-4033-09.json") is True
        assert validate_filename("HFD_2025_ref-123__mal-7343-24.pdf") is True

    def test_validate_filename_invalid(self):
        """Ogiltigt filnamn."""
        assert validate_filename("invalid.json") is False
        assert validate_filename("HFD_2011_ref-1__mal-4033-09.json") is False  # Inte 3 siffror
        assert validate_filename("HFD_2011_ref-001__mal-4033.json") is False  # Saknar årssuffix


class TestReferatnummerParsning:
    """Tester för referatnummerparsning."""

    def test_parse_referat_nummer_hfd(self):
        """HFD-referat."""
        year, ref_no = parse_referat_nummer("HFD 2011 ref. 1")
        assert year == 2011
        assert ref_no == 1

    def test_parse_referat_nummer_hfd_high_number(self):
        """HFD-referat med högre nummer."""
        year, ref_no = parse_referat_nummer("HFD 2025 ref. 123")
        assert year == 2025
        assert ref_no == 123

    def test_parse_referat_nummer_ra(self):
        """RÅ-referat (Regeringsrätten)."""
        year, ref_no = parse_referat_nummer("RÅ 2010 ref. 8")
        assert year == 2010
        assert ref_no == 8

    def test_parse_referat_nummer_invalid(self):
        """Ogiltigt format."""
        with pytest.raises(ValueError):
            parse_referat_nummer("Invalid format")

    def test_parse_referat_nummer_missing_ref(self):
        """Saknar 'ref.'."""
        with pytest.raises(ValueError):
            parse_referat_nummer("HFD 2011 1")
