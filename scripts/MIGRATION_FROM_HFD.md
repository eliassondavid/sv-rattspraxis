# MIGRATION FROM HFD-RATTSPRAXIS

**Datum:** 2026-02-19  
**Syfte:** Dokumentera migrering från gamla HFD-strukturen till sv-rattspraxis

---

## 1. FÖRBEREDELSER

### 1.1 Gamla strukturen
```
/Users/davideliasson/Downloads/hfd-rattspraxis/
├── api_client.py
├── models.py
├── harvester.py
├── naming.py
├── verify.py
├── cli.py (?)
├── html_parser.py (?)
├── export.py (?)
└── tests/ (?)
    ├── test_*.py
    └── fixtures/
```

### 1.2 Nya strukturen
```
sv-rattspraxis/
├── src/sv_rattspraxis/
│   ├── __init__.py (redan klar)
│   ├── api_client.py → MIGRERA
│   ├── models.py → MIGRERA
│   ├── harvester.py → MIGRERA
│   ├── naming.py → MIGRERA
│   ├── verify.py → MIGRERA
│   ├── cli.py → MIGRERA/SKAPA
│   ├── html_parser.py → MIGRERA (om finns)
│   └── export.py → MIGRERA (om finns)
└── tests/
    ├── conftest.py → SKAPA
    ├── test_*.py → MIGRERA
    └── fixtures/ → MIGRERA
```

---

## 2. MIGRERINGSALTERNATIV

### Alternativ A: Automatiskt skript (rekommenderat)

```bash
# 1. Ladda ner och placera migrate_hfd_code.sh i scripts/
cd sv-rattspraxis
chmod +x scripts/migrate_hfd_code.sh

# 2. Kör skriptet
./scripts/migrate_hfd_code.sh

# 3. Kontrollera resultat
ls -la src/sv_rattspraxis/
```

**Skriptet gör:**
- ✅ Kopierar alla Python-filer från gamla strukturen
- ✅ Lägger till Apache 2.0-header i alla filer
- ✅ Kopierar tester och fixtures (om de finns)
- ✅ Rapporterar vad som migerades

### Alternativ B: Manuell migrering

```bash
# 1. Gå till sv-rattspraxis root
cd sv-rattspraxis

# 2. Kopiera filer en och en
cp /Users/davideliasson/Downloads/hfd-rattspraxis/api_client.py \
   src/sv_rattspraxis/

cp /Users/davideliasson/Downloads/hfd-rattspraxis/models.py \
   src/sv_rattspraxis/

# ... etc för alla filer
```

**Sedan:**
1. Öppna varje fil i editor
2. Lägg till Apache-header (se mall nedan)
3. Kontrollera imports

---

## 3. APACHE 2.0-HEADER MALL

Lägg till detta **överst i varje Python-fil** (före imports):

```python
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
Modulens docstring här...
"""

import ...
```

---

## 4. FILSPECIFIKA ÄNDRINGAR

### 4.1 `__init__.py` (redan fixad)

Inga ändringar behövs - redan uppdaterad med Apache 2.0.

### 4.2 `api_client.py`

**Förväntade ändringar:**
- Lägg till Apache-header
- Kontrollera att `BASE_URL` är korrekt: 
  `https://rattspraxis.etjanst.domstol.se/api/v1/`
- Kontrollera User-Agent

**Exempel:**
```python
# Apache-header här...

"""API-klient för Domstolsverkets REST-API."""

from typing import Any, Optional
import httpx
from pydantic import BaseModel

BASE_URL = "https://rattspraxis.etjanst.domstol.se/api/v1/"
USER_AGENT = "SVRattspraxisHarvester/1.0 (Access to Justice Research)"
```

### 4.3 `models.py`

**Förväntade ändringar:**
- Lägg till Apache-header
- Kontrollera att alla Pydantic-modeller är v2-kompatibla
- Lägg till `DomstolKod` enum (alla 22 domstolar)

**Exempel:**
```python
# Apache-header här...

"""Pydantic-modeller för rättspraxis."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class DomstolKod(str, Enum):
    HFD = "HFD"
    HDO = "HDO"
    ADO = "ADO"
    REGR = "REGR"
    # ... alla 22 domstolar

class PubliceringsTyp(str, Enum):
    REFERAT = "REFERAT"
    NOTIS = "NOTIS"
    DOM_ELLER_BESLUT = "DOM_ELLER_BESLUT"
    PROVNINGSTILLSTAND = "PROVNINGSTILLSTAND"
    FORHANDSAVGORANDE = "FORHANDSAVGORANDE"

class Publikation(BaseModel):
    id: str
    referatNummerLista: List[str]
    # ... resten
```

### 4.4 `harvester.py`

**Förväntade ändringar:**
- Lägg till Apache-header
- Parametrisera `domstolKod` (inte hårdkodat "HFD")
- Lägg till `courts.py`-integration (sker i Fas 1)

**Nuvarande:** HFD-specifik  
**Framtida:** Generaliserad (Fas 1)

### 4.5 `naming.py`

**Förväntade ändringar:**
- Lägg till Apache-header
- Generalisera från `HFD_` till `{DOMSTOL}_` prefix
- Stöd för HDO-målnummerformat (bokstavsprefix)

**Exempel:**
```python
def generate_filename(
    domstol: str,
    year: int,
    ref_num: int,
    malnummer: str
) -> str:
    """
    Generera filnamn enligt konvention.
    
    Format: {DOMSTOL}_{YEAR}_ref-{NNN}__mal-{MALNR}.json
    
    Exempel:
        >>> generate_filename("HFD", 2023, 42, "3660-22")
        'HFD_2023_ref-042__mal-3660-22.json'
    """
    return f"{domstol}_{year}_ref-{ref_num:03d}__mal-{malnummer}.json"
```

### 4.6 `verify.py`

**Förväntade ändringar:**
- Lägg till Apache-header
- Parametrisera domstol
- Sekvenskontroll per domstol

### 4.7 `cli.py`

**Om den finns:** Migrera och lägg till Apache-header  
**Om den saknas:** Skapas i Fas 1

CLI ska använda `click` eller `typer`:

```python
# Apache-header här...

"""CLI för sv-rattspraxis."""

import click
from sv_rattspraxis.harvester import harvest

@click.group()
def main():
    """sv-rp: Harvester för svensk rättspraxis."""
    pass

@main.command()
@click.option('--court', required=True, help='Domstolskod (t.ex. HFD)')
@click.option('--type', default='referat', help='Publikationstyp')
def harvest_cmd(court: str, type: str):
    """Harvesta publikationer från en domstol."""
    click.echo(f"Harvestar {court} {type}...")
    # ... implementation
```

---

## 5. TESTFILER

### 5.1 `conftest.py` (skapa om den saknas)

```python
# Apache-header här...

"""Pytest fixtures för sv-rattspraxis."""

import pytest
from pathlib import Path

@pytest.fixture
def fixtures_dir() -> Path:
    """Path till fixtures-mappen."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_hfd_response(fixtures_dir):
    """Ladda sample HFD API-svar."""
    import json
    with open(fixtures_dir / "sample_hfd_response.json") as f:
        return json.load(f)
```

### 5.2 Migrera befintliga tester

Kopiera och lägg till Apache-header i:
- `test_api_client.py`
- `test_models.py`
- `test_naming.py`
- `test_verify.py`
- etc.

---

## 6. KONTROLLISTA EFTER MIGRERING

### 6.1 Filkontroll

```bash
# Kontrollera att alla filer finns
ls -la src/sv_rattspraxis/

# Förväntat:
# __init__.py (redan klar)
# api_client.py
# models.py
# harvester.py
# naming.py
# verify.py
# cli.py (om den fanns)
```

### 6.2 Header-kontroll

```bash
# Kontrollera att alla filer har Apache-header
grep -l "Licensed under the Apache License" src/sv_rattspraxis/*.py

# Alla .py-filer ska visas
```

### 6.3 Import-kontroll

```bash
# Installera paket
pip install -e ".[dev]"

# Testa import
python -c "from sv_rattspraxis import APIClient, Publikation; print('OK')"
```

### 6.4 Test-kontroll

```bash
# Kör tester
make test

# Eller:
pytest -v
```

### 6.5 Lint-kontroll

```bash
# Kör linting
make lint

# Eller:
ruff check src/ tests/
mypy src/
```

---

## 7. GIT COMMIT

När allt är OK:

```bash
# Lägg till alla filer
git add .

# Commit med beskrivande meddelande
git commit -m "feat: migrate HFD harvester code to sv-rattspraxis

- Migrated all Python files from hfd-rattspraxis
- Added Apache 2.0 headers to all source files
- Updated imports and structure
- Tests migrated and passing

Migration includes:
- api_client.py (REST-klient)
- models.py (Pydantic-modeller)
- harvester.py (HFD-specifik, generaliseras i Fas 1)
- naming.py (filnamnskonvention)
- verify.py (integritetskontroll)
- All tests and fixtures

Related: HFD harvester v0.0.1 (~1,900 lines, 1,117 referat)"
```

---

## 8. NÄSTA STEG EFTER MIGRERING

### Fas 0 (Gemini)
- API-katalogisering för alla 22 domstolar
- Skapa `api_catalog.json`

### Fas 1 (Sonnet 4.5)
- Generalisera harvester
- Skapa `courts.py` med domstolskonfiguration
- Uppdatera `cli.py` med `--court` parameter

### Fas 1b (Opus 4.6)
- Skapa `malnummer.py` med robust parser
- Stöd för alla domstolars målnummerformat

---

## 9. FELSÖKNING

### Problem: Import-fel efter migrering

```bash
# Kontrollera att paket är installerat
pip show sv-rattspraxis

# Om inte, installera:
pip install -e .
```

### Problem: Apache-header saknas i vissa filer

```bash
# Hitta filer utan header
for file in src/sv_rattspraxis/*.py; do
  if ! grep -q "Licensed under the Apache License" "$file"; then
    echo "Saknar header: $file"
  fi
done
```

### Problem: Tester failar efter migrering

```bash
# Kör ett test i taget för att hitta problemet
pytest tests/test_api_client.py -v
pytest tests/test_models.py -v
# etc.
```

---

## 10. ROLLBACK (om något går fel)

```bash
# Ta bort alla migrerade filer
rm -rf src/sv_rattspraxis/*.py
rm -rf tests/test_*.py

# Behåll bara __init__.py
git checkout src/sv_rattspraxis/__init__.py

# Börja om
```

---

**Lycka till med migreringen!** 🚀

Vid problem, se FELSÖKNING-sektionen eller öppna en issue på GitHub.
