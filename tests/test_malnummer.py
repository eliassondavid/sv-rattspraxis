"""Tester för robust målnummerparsning (Fas 1B)."""

from sv_rattspraxis.naming import (
    MalnummerParser,
    generate_filename,
    parse_referat_nummer,
    sanitize_malnummer_for_filename,
    validate_filename,
)


def parse(text: str) -> list[str]:
    all_malnummer, _ = MalnummerParser.parse_malnummer_lista([text])
    return all_malnummer


def parse_malnummer_lista(raw_lista: list[str]) -> tuple[list[str], str]:
    return MalnummerParser.parse_malnummer_lista(raw_lista)


class TestMalnummerParserHFD:
    """HFD-specifika tester från HFD-mal_nr.md."""

    def test_single_basic(self):
        assert parse("4033-09") == ["4033-09"]

    def test_lista_komma(self):
        assert parse("6963-15, 6969-15") == ["6963-15", "6969-15"]

    def test_lista_och(self):
        assert parse("6980-24 och 6981-24") == ["6980-24", "6981-24"]

    def test_lista_samt(self):
        assert parse("6980-24 samt 6981-24") == ["6980-24", "6981-24"]

    def test_split_list_placeholder_a_samt_b(self):
        assert MalnummerParser.split_list("A samt B") == ["A", "B"]

    def test_intervall_endash(self):
        assert parse("6107–6109-23") == ["6107-23", "6108-23", "6109-23"]

    def test_intervall_doubledash(self):
        assert parse("6159--6160-14") == ["6159-14", "6160-14"]

    def test_intervall_singledash(self):
        assert parse("4569-4571-22") == ["4569-22", "4570-22", "4571-22"]

    def test_intervall_reverse_order_swappas(self):
        assert parse("6109--6107-23") == ["6107-23", "6108-23", "6109-23"]

    def test_intervall_med_mellanrum(self):
        assert parse("6107 -- 6109 - 23") == ["6107-23", "6108-23", "6109-23"]

    def test_kombination_1(self):
        result = parse("6578-14, 6159--6160-14")
        assert result == ["6578-14", "6159-14", "6160-14"]

    def test_kombination_2(self):
        result = parse("7550–7558-21 samt 664–669-22")
        assert "7550-21" in result
        assert "7558-21" in result
        assert "664-22" in result
        assert "669-22" in result
        assert len(result) == 15

    def test_med_prefix_mal_nr(self):
        assert parse("Mål nr. 4033-09") == ["4033-09"]

    def test_med_prefix_mal_kolon(self):
        assert parse("Mål: 4033-09 och 4034-09") == ["4033-09", "4034-09"]

    def test_flera_rader_i_inputlista(self):
        all_mal, primary = parse_malnummer_lista(["4033-09", "6159--6160-14"])
        assert all_mal == ["4033-09", "6159-14", "6160-14"]
        assert primary == "4033-09"


class TestMalnummerParserHDHovratt:
    """HD/hovrätt-prefix från courts.py och api_catalog.json."""

    def test_t_prefix(self):
        assert parse("T 1234-22") == ["T 1234-22"]

    def test_b_prefix(self):
        assert parse("B 5678-21") == ["B 5678-21"]

    def test_o_prefix(self):
        assert parse("Ö 9012-23") == ["Ö 9012-23"]

    def test_oa_prefix(self):
        assert parse("ÖÄ 717-20") == ["ÖÄ 717-20"]

    def test_a_prefix(self):
        assert parse("Ä 7634-24") == ["Ä 7634-24"]

    def test_k_prefix(self):
        assert parse("K 13251-25") == ["K 13251-25"]

    def test_whitespace_normalisering_prefix(self):
        assert parse("T   1234-22") == ["T 1234-22"]

    def test_langre_prefix_pmt(self):
        assert parse("PMT 10755-25") == ["PMT 10755-25"]

    def test_langre_prefix_pma(self):
        assert parse("PMÄ 16563-24") == ["PMÄ 16563-24"]

    def test_langre_prefix_um(self):
        assert parse("UM 12369-24") == ["UM 12369-24"]


class TestMalnummerParserAD:
    """AD-specifika tester."""

    def test_a_slash(self):
        assert parse("A 153/24") == ["A 153/24"]

    def test_a_slash_whitespace(self):
        assert parse("A   153/24") == ["A 153/24"]


class TestMalnummerParserMODMMOD:
    """MÖD/MMOD-specifika tester."""

    def test_m_prefix(self):
        assert parse("M 4256-10") == ["M 4256-10"]

    def test_m_prefix_femsiffrig_lopnummer(self):
        assert parse("M 11808-23") == ["M 11808-23"]


class TestMalnummerParserMDO:
    """MDO-specifika tester."""

    def test_year_format_one_digit(self):
        assert parse("2016-9") == ["2016-9"]

    def test_year_format_two_digits(self):
        assert parse("2016-12") == ["2016-12"]


class TestMalnummerParserPbrRhn:
    """Kortformat från PBR/RHN."""

    def test_pbr_nn_nnn(self):
        assert parse("10-292") == ["10-292"]

    def test_rhn_nn_nn(self):
        assert parse("33-09") == ["33-09"]

    def test_kammarratt_standard(self):
        assert parse("787-01") == ["787-01"]


class TestMalnummerParserEdgeCases:
    """Edge cases och defensivt beteende."""

    def test_empty_list(self):
        all_mal, primary = parse_malnummer_lista([])
        assert all_mal == []
        assert primary == "UNKNOWN"

    def test_invalid_format(self):
        all_mal, primary = parse_malnummer_lista(["garbage"])
        assert all_mal == []
        assert primary == "UNKNOWN"

    def test_placeholder_tokens_parsas_inte_som_malnummer(self):
        all_mal, primary = parse_malnummer_lista(["A samt B"])
        assert all_mal == []
        assert primary == "UNKNOWN"

    def test_none_i_lista_hanteras(self):
        all_mal, primary = parse_malnummer_lista([None, "4033-09"])  # type: ignore[list-item]
        assert all_mal == ["4033-09"]
        assert primary == "4033-09"

    def test_parse_single_no_match(self):
        assert MalnummerParser.parse_single("inte ett målnummer") is None

    def test_parse_range_no_match(self):
        assert MalnummerParser.parse_range("4033-09") is None

    def test_parse_range_tuple(self):
        assert MalnummerParser.parse_range("6159--6160-14") == (6159, 6160, "14")

    def test_expand_range_swappad_ordning(self):
        assert MalnummerParser.expand_range(6160, 6159, "14") == ["6159-14", "6160-14"]

    def test_normalize_interval_chars(self):
        assert MalnummerParser.normalize_interval_chars("6107–6109-23") == "6107--6109-23"

    def test_split_list_case_insensitiv(self):
        assert MalnummerParser.split_list("4033-09 OCH 4034-09") == ["4033-09", "4034-09"]

class TestNamingHelpers:
    """Tester för hjälpfunktioner i naming.py."""

    def test_sanitize_malnummer_for_filename(self):
        assert sanitize_malnummer_for_filename(" UM 12369/24 ") == "UM12369-24"

    def test_sanitize_malnummer_empty(self):
        assert sanitize_malnummer_for_filename("   ") == "UNKNOWN"

    def test_generate_filename_json(self):
        filename = generate_filename("hfd", 2025, 49, "6980-24")
        assert filename == "HFD_2025_ref-049__mal-6980-24.json"

    def test_generate_filename_pdf(self):
        filename = generate_filename("HFD", 2025, 13, "6107--6109-23", extension="pdf")
        assert filename == "HFD_2025_ref-013__mal-6107--6109-23.pdf"

    def test_generate_filename_empty_domstol(self):
        try:
            generate_filename("", 2025, 1, "4033-09")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for empty domstol")

    def test_parse_referat_nummer_hfd(self):
        assert parse_referat_nummer("HFD 2024 ref. 12") == (2024, 12)

    def test_parse_referat_nummer_ad(self):
        assert parse_referat_nummer("AD 2023 nr 7") == (2023, 7)

    def test_parse_referat_nummer_rh(self):
        assert parse_referat_nummer("RH 2021:9") == (2021, 9)

    def test_parse_referat_nummer_nja(self):
        assert parse_referat_nummer("NJA 2019 s. 45") == (2019, 45)

    def test_parse_referat_nummer_fallback(self):
        assert parse_referat_nummer("Okänd 2018 text 99") == (2018, 99)

    def test_parse_referat_nummer_error(self):
        try:
            parse_referat_nummer("ingen träff")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError when referatnummer cannot be parsed")

    def test_validate_filename_true(self):
        assert validate_filename("HFD_2025_ref-049__mal-6980-24.pdf")

    def test_validate_filename_false(self):
        assert not validate_filename("hfd_2025_ref-049__mal-6980-24.pdf")
