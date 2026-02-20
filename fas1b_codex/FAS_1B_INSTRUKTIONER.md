# FAS 1B — MÅLNUMMERPARSNING

**Modell:** GPT-5.3-Codex  
**Tidsuppskattning:** 1-2 timmar  
**Input:** HFD-mal_nr.md + befintlig naming.py + api_catalog.json edge cases

---

## BAKGRUND

HFD-målnummer är välstrukturerade men har många varianter:
- Single: `4033-09`
- Lista: `6963-15, 6969-15`
- Intervall: `6107–6109-23` (en-dash)
- Intervall: `6159--6160-14` (dubbel-dash)
- Kombinationer: `6578-14, 6159--6160-14`

Andra domstolar har andra format:
- HD: `T 1234-22`, `B 5678-21`, `Ö 9012-23`
- AD: `A 153/24`
- MÖD: `M 4256-10`
- MMOD: `M 12345-23`, `UM 12369-24`
- MDO: `2016-9`

**Problem med nuvarande implementation:**
- Parsern extraherar korrekt men testar inte alla varianter
- Behöver robustare hantering av prefix (T, B, M, UM, etc.)
- Behöver expansion av ranges med olika intervalltecken

---

## UPPGIFTER

### 1. Analysera HFD-mal_nr.md

Dokumentera alla varianter:
- Grundformat
- Listor (komma, "och", "samt")
- Intervall (–, --, -)
- Kombinationer

### 2. Förbättra MalnummerParser

**Nuvarande implementation (naming.py):**
```python
class MalnummerParser:
    SINGLE_PATTERNS = (...)
    RANGE_PATTERN = (...)
    
    @classmethod
    def parse_single(cls, token: str) -> str | None: ...
    
    @classmethod
    def parse_range(cls, token: str) -> tuple[int, int, str] | None: ...
    
    @classmethod
    def expand_range(cls, start: int, end: int, year: str) -> list[str]: ...
    
    @classmethod
    def parse_malnummer_lista(cls, raw_lista: list[str]) -> tuple[list[str], str]: ...
```

**Förbättringar:**
1. ✅ Hantera alla prefix korrekt (T, B, M, UM, PMT, etc.)
2. ✅ Normalisera alla intervalltecken (–, --, -)
3. ✅ Expandera ranges korrekt
4. ✅ Behåll originalform i metadata men normalisera för filnamn

### 3. Skapa omfattande testsvit

**Minst 30 testfall:**
- HFD: single, lista, intervall, kombinationer
- HD: T/B/Ö-prefix
- AD: A-prefix med slash
- MÖD: M-prefix
- MDO: År-format (2016-9)
- Edge cases: tomma listor, ogiltiga format

### 4. Dokumentation

Skapa `MALNUMMER_FORMAT.md`:
- Format per domstol
- Exempel
- Normaliseringsregler
- Testresultat

---

## TESTNING
```bash
# Kör alla tester
pytest tests/test_malnummer.py -v

# Coverage ska vara ≥95% för MalnummerParser
pytest tests/test_malnummer.py --cov=sv_rattspraxis.naming --cov-report=term
```

---

## LEVERABLER

1. **naming.py** (uppdaterad) — Förbättrad MalnummerParser
2. **test_malnummer.py** (ny) — Omfattande testsvit (30+ tester)
3. **MALNUMMER_FORMAT.md** (ny) — Dokumentation
4. **README_FAS1B.md** (ny) — Ändringslogg

---

## KVALITETSKRAV

✅ Alla befintliga tester passar (33/33)  
✅ Nya tester passar (30+/30+)  
✅ Coverage ≥95% för MalnummerParser  
✅ Alla HFD-varianter från HFD-mal_nr.md hanterade  
✅ HD/AD/MÖD/MDO-format verifierade mot api_catalog.json  
✅ Code style konsistent (ruff + mypy)
