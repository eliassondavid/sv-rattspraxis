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
Tester för Pydantic-modeller.

Testar:
- Deserialisering från API-JSON
- Validering av fält
- Model dump
"""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from sv_rattspraxis.models import (
    Domstol,
    Lagrum,
    Litteratur,
    MasterListEntry,
    Publication,
    SearchFilter,
    SearchRequest,
)


class TestDomstol:
    """Tester för Domstol-modell."""

    def test_domstol_valid(self):
        """Giltig domstol."""
        domstol = Domstol(
            domstolKod="HFD",
            domstolNamn="Högsta förvaltningsdomstolen",
        )
        assert domstol.domstolKod == "HFD"
        assert domstol.domstolNamn == "Högsta förvaltningsdomstolen"

    def test_domstol_missing_field(self):
        """Saknat fält."""
        with pytest.raises(ValidationError):
            Domstol(domstolKod="HFD")


class TestLagrum:
    """Tester för Lagrum-modell."""

    def test_lagrum_valid(self):
        """Giltigt lagrum."""
        lagrum = Lagrum(
            referens="3 kap. 6 § miljöbalken (1998:808)",
            sfsNummer="1998:808",
        )
        assert lagrum.referens == "3 kap. 6 § miljöbalken (1998:808)"
        assert lagrum.sfsNummer == "1998:808"


class TestLitteratur:
    """Tester för Litteratur-modell."""

    def test_litteratur_valid(self):
        """Giltig litteratur."""
        lit = Litteratur(
            forfattare="Bengtsson m.fl.",
            titel="Miljöbalken, En kommentar s. 3:15",
        )
        assert lit.forfattare == "Bengtsson m.fl."
        assert lit.titel == "Miljöbalken, En kommentar s. 3:15"


class TestPublication:
    """Tester för Publication-modell."""

    def test_publication_minimal(self):
        """Minimal giltig publikation."""
        pub = Publication(
            id=UUID("12345678-1234-1234-1234-123456789abc"),
            typ="REFERAT",
            domstol=Domstol(
                domstolKod="HFD",
                domstolNamn="Högsta förvaltningsdomstolen",
            ),
            avgorandedatum="2011-01-26",
            publiceringstid=datetime.fromisoformat("2011-05-04T15:13:18"),
        )
        assert pub.typ == "REFERAT"
        assert pub.domstol.domstolKod == "HFD"

    def test_publication_full(self):
        """Fullständig publikation."""
        pub = Publication(
            id=UUID("12345678-1234-1234-1234-123456789abc"),
            typ="REFERAT",
            domstol=Domstol(
                domstolKod="HFD",
                domstolNamn="Högsta förvaltningsdomstolen",
            ),
            referatNummerLista=["HFD 2011 ref. 1"],
            malNummerLista=["4033-09", "4034-09"],
            avgorandedatum="2011-01-26",
            publiceringstid=datetime.fromisoformat("2011-05-04T15:13:18"),
            sammanfattning="Kort beskrivning...",
            innehall="<p>Full HTML...</p>",
            lagrumLista=[
                Lagrum(
                    referens="3 kap. 6 § miljöbalken (1998:808)",
                    sfsNummer="1998:808",
                )
            ],
            litteraturLista=[
                Litteratur(
                    forfattare="Bengtsson m.fl.",
                    titel="Miljöbalken, En kommentar s. 3:15",
                )
            ],
            nyckelordLista=["Mervärdesskatt"],
            rattsomradeLista=["Skatt"],
            arVagledande=True,
        )
        assert len(pub.malNummerLista) == 2
        assert len(pub.lagrumLista) == 1
        assert len(pub.litteraturLista) == 1
        assert pub.arVagledande is True


class TestSearchRequest:
    """Tester för SearchRequest-modell."""

    def test_search_request_default(self):
        """Default SearchRequest."""
        req = SearchRequest()
        assert req.antalPerSida == 100
        assert req.asc is True
        assert req.sidIndex == 0
        assert req.filter.domstolKodLista == ["HFD"]
        assert req.filter.avgorandeTypLista == ["REFERAT"]

    def test_search_request_custom(self):
        """Custom SearchRequest."""
        req = SearchRequest(
            antalPerSida=50,
            asc=False,
            sidIndex=2,
            filter=SearchFilter(
                domstolKodLista=["HDO"],
                avgorandeTypLista=["NOTIS"],
            ),
        )
        assert req.antalPerSida == 50
        assert req.asc is False
        assert req.sidIndex == 2
        assert req.filter.domstolKodLista == ["HDO"]

    def test_search_request_validation(self):
        """Validering av antalPerSida."""
        with pytest.raises(ValidationError):
            SearchRequest(antalPerSida=0)  # < 1

        with pytest.raises(ValidationError):
            SearchRequest(antalPerSida=101)  # > 100


class TestMasterListEntry:
    """Tester för MasterListEntry-modell."""

    def test_masterlist_entry_valid(self):
        """Giltig MasterListEntry."""
        entry = MasterListEntry(
            api_id=UUID("12345678-1234-1234-1234-123456789abc"),
            domstol="HFD",
            typ="REFERAT",
            referat_nummer="HFD 2011 ref. 1",
            year=2011,
            ref_no=1,
            ref_no_padded="001",
            malnummer_primart="4033-09",
            avgorandedatum="2011-01-26",
            filnamn_json="HFD_2011_ref-001__mal-4033-09.json",
            sha256_json="abc123...",
            harvest_timestamp="2026-02-18T14:30:00Z",
        )
        assert entry.year == 2011
        assert entry.ref_no == 1
        assert entry.ref_no_padded == "001"
