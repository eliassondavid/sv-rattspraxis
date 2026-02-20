# FAS 1 — GENERALISERA HARVESTER

**Modell:** GPT-5.3-Codex  
**Tidsuppskattning:** 2-4 timmar  
**Input:** Befintlig HFD-kod + api_catalog.json

---

## BAKGRUND

HFD-harvestern är klar (1,117 referat). Nu ska den generaliseras till alla 22 domstolar.

**Befintlig kod:**
- `src/sv_rattspraxis/harvester.py` (HFD-specifik)
- `src/sv_rattspraxis/naming.py` (HFD-prefix)
- `src/sv_rattspraxis/api_client.py` (redan generisk)
- `src/sv_rattspraxis/cli.py` (hårdkodad HFD)

---

## UPPGIFTER

### 1. Skapa `courts.py`

Baserat på `api_catalog.json`, skapa en konfigurationsfil:
```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class CourtConfig:
    kod: str
    namn: str
    referat_format: str  # "HFD YYYY ref. N"
    malnummer_format: str  # "NNNN-NN" eller "X NNNN-NN" (HDO)
    prioritet: int  # 1=högst (HDO, REGR), 5=lägst
    volymer: Dict[str, int]  # {"REFERAT": 1342, ...}
    har_innehall: bool  # True om fulltext finns
    har_bilagor: bool
    kommentar: str = ""

# Alla 22 domstolar konfigurerade
COURTS = {
    "HFD": CourtConfig(...),
    "HDO": CourtConfig(...),
    ...
}
```

### 2. Generalisera `harvester.py`

Från:
```python
class HFDHarvester:
    def __init__(self, api_client, from_year=2011, to_year=None, typ="REFERAT"):
        self.domstol = "HFD"  # Hårdkodad
```

Till:
```python
class DomstolHarvester:
    def __init__(self, api_client, domstol_kod: str, from_year=2011, to_year=None, typ="REFERAT"):
        self.domstol = domstol_kod  # Parametriserad
        self.config = COURTS[domstol_kod]
```

### 3. Generalisera `naming.py`

Från:
```python
def generate_filename(year: int, ref_no: int, malnr: str) -> str:
    return f"HFD_{year}_ref-{ref_no:03d}__mal-{malnr}.json"
```

Till:
```python
def generate_filename(domstol: str, year: int, ref_no: int, malnr: str) -> str:
    return f"{domstol}_{year}_ref-{ref_no:03d}__mal-{malnr}.json"
```

### 4. Uppdatera `cli.py`

Lägg till `--court` parameter:
```python
@app.command()
def harvest(
    court: str = typer.Option("HFD", help="Domstolskod (HFD, HDO, ADO, ...)"),
    typ: str = typer.Option("REFERAT", help="Typ av avgörande"),
    from_year: int = typer.Option(2011, help="Startår"),
):
    if court not in COURTS:
        console.print(f"❌ Okänd domstol: {court}", style="red")
        raise typer.Exit(1)
    
    harvester = DomstolHarvester(api_client, court, from_year, typ=typ)
    ...
```

---

## TESTNING

Efter refactoring, testa:
```bash
# HFD ska fortfarande fungera (bakåtkompatibelt)
sv-rp harvest --court HFD --typ REFERAT

# Testa HDO (5,518 referat)
sv-rp harvest --court HDO --typ REFERAT --from-year 2020
```

---

## LEVERABLER

1. **courts.py** — Komplett konfiguration för alla 22 domstolar
2. **harvester.py** (uppdaterad) — Domstol-agnostisk
3. **naming.py** (uppdaterad) — Generaliserad filnamnskonvention
4. **cli.py** (uppdaterad) — `--court` parameter
5. **README_FAS1.md** — Dokumentation av ändringar

---

## KVALITETSKRAV

✅ Alla befintliga tester passar (33/33)  
✅ HFD-harvesting fortfarande fungerar (bakåtkompatibilitet)  
✅ HDO kan harvestas med `--court HDO`  
✅ Inga hårdkodade domstolskoder kvar  
✅ Code style konsistent (ruff + mypy passar)
