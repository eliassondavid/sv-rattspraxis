"""Tests for FAS 1C: non-referat publication types and PDF extraction."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sv_rattspraxis.cli import harvest
from sv_rattspraxis.harvester import DomstolHarvester, SUPPORTED_HARVEST_TYPES
from sv_rattspraxis.naming import (
    generate_filename_dom,
    generate_filename_for_type,
    generate_filename_notis,
    generate_filename_pt,
)
from sv_rattspraxis.pdf_extractor import extract_pdf_text


class _DummyClient:
    async def search(self, request: dict[str, object]) -> dict[str, object]:
        _ = request
        return {"total": 0, "publiceringLista": []}


def test_naming_formats_for_new_types() -> None:
    assert generate_filename_dom("HDO", 2024, "T 123-24") == "HDO_2024_dom__mal-T123-24.json"
    assert generate_filename_pt("HFD", 2024, "3020-24") == "HFD_2024_pt__mal-3020-24.json"
    assert (
        generate_filename_notis("HFD", 2023, 12, "4460-25")
        == "HFD_2023_not-012__mal-4460-25.json"
    )

    assert (
        generate_filename_for_type("HFD", "DOM_ELLER_BESLUT", 2024, 99, "3020-24")
        == "HFD_2024_dom__mal-3020-24.json"
    )
    assert (
        generate_filename_for_type("HFD", "PROVNINGSTILLSTAND", 2024, 99, "3020-24")
        == "HFD_2024_pt__mal-3020-24.json"
    )
    assert generate_filename_for_type("HFD", "NOTIS", 2024, 3, "3020-24").startswith(
        "HFD_2024_not-003__mal-3020-24."
    )


def test_fallback_sequence_is_per_type_and_year(tmp_path: Path) -> None:
    harvester = DomstolHarvester(data_root=tmp_path, api_client=_DummyClient(), domstol_kod="HFD")

    ref1, year1, no1 = harvester._fallback_referat("2024-01-01", "DOM_ELLER_BESLUT")
    ref2, year2, no2 = harvester._fallback_referat("2024-02-01", "DOM_ELLER_BESLUT")
    ref3, year3, no3 = harvester._fallback_referat("2024-03-01", "PROVNINGSTILLSTAND")
    ref4, year4, no4 = harvester._fallback_referat("2025-01-01", "DOM_ELLER_BESLUT")

    assert (year1, no1, ref1) == (2024, 1, "HFD 2024 dom 1")
    assert (year2, no2, ref2) == (2024, 2, "HFD 2024 dom 2")
    assert (year3, no3, ref3) == (2024, 1, "HFD 2024 pt 1")
    assert (year4, no4, ref4) == (2025, 1, "HFD 2025 dom 1")


@pytest.mark.asyncio
async def test_process_publication_dom_uses_fallback_and_dom_filename(tmp_path: Path) -> None:
    harvester = DomstolHarvester(
        data_root=tmp_path,
        api_client=_DummyClient(),
        domstol_kod="HFD",
        typ="DOM_ELLER_BESLUT",
    )
    publication = {
        "id": "pub-1",
        "typ": "DOM_ELLER_BESLUT",
        "avgorandedatum": "2024-05-20",
        "referatNummerLista": [],
        "malNummerLista": ["3020-24"],
        "domstol": {"domstolKod": "HFD"},
        "innehall": "<p>domtext</p>",
    }

    entry = await harvester.process_publication(publication)
    assert entry is not None
    assert entry.referat_nummer == "HFD 2024 dom 1"
    assert entry.filnamn_json == "HFD_2024_dom__mal-3020-24.json"


@pytest.mark.asyncio
async def test_process_publication_notis_uses_notis_filename(tmp_path: Path) -> None:
    harvester = DomstolHarvester(
        data_root=tmp_path,
        api_client=_DummyClient(),
        domstol_kod="HFD",
        typ="NOTIS",
    )
    publication = {
        "id": "pub-2",
        "typ": "NOTIS",
        "avgorandedatum": "2023-01-03",
        "referatNummerLista": [],
        "malNummerLista": ["4460-25"],
        "domstol": {"domstolKod": "HFD"},
        "innehall": "<p>notis</p>",
    }

    entry = await harvester.process_publication(publication)
    assert entry is not None
    assert entry.referat_nummer == "HFD 2023 not. 1"
    assert entry.filnamn_json == "HFD_2023_not-001__mal-4460-25.json"


@pytest.mark.asyncio
async def test_hdo_dom_without_innehall_is_enriched_from_pdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_extract_pdf_text(api_client: object, bilaga_id: str) -> str:
        _ = api_client
        assert bilaga_id == "bilaga-42"
        return "Text från PDF"

    monkeypatch.setattr("sv_rattspraxis.harvester.extract_pdf_text", _fake_extract_pdf_text)

    harvester = DomstolHarvester(
        data_root=tmp_path,
        api_client=_DummyClient(),
        domstol_kod="HDO",
        typ="DOM_ELLER_BESLUT",
    )
    publication = {
        "id": "pub-3",
        "typ": "DOM_ELLER_BESLUT",
        "avgorandedatum": "2024-06-30",
        "referatNummerLista": [],
        "malNummerLista": ["T 123-24"],
        "domstol": {"domstolKod": "HDO"},
        "innehall": "",
        "bilagaLista": [{"fillagringId": "bilaga-42"}],
    }

    entry = await harvester.process_publication(publication)
    assert entry is not None
    saved = json.loads((tmp_path / "raw" / entry.filnamn_json).read_text(encoding="utf-8"))
    assert saved["innehall"] == "Text från PDF"


@pytest.mark.asyncio
async def test_pdf_extractor_fetches_bilaga_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Response:
        def __init__(self) -> None:
            self.content = b"%PDF-fake"

        def raise_for_status(self) -> None:
            return None

    class _Client:
        def __init__(self) -> None:
            self.urls: list[str] = []

        async def get(self, url: str) -> _Response:
            self.urls.append(url)
            return _Response()

    client = _Client()
    monkeypatch.setattr("sv_rattspraxis.pdf_extractor._extract_text_from_pdf_bytes", lambda _: "ok")

    text = await extract_pdf_text(client, "abc123")
    assert text == "ok"
    assert client.urls == ["/api/v1/bilagor/abc123"]


def test_cli_type_choice_contains_new_types() -> None:
    type_option = next(param for param in harvest.params if param.name == "harvest_type")
    assert sorted(type_option.type.choices) == sorted(SUPPORTED_HARVEST_TYPES)

