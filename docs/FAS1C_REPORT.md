# FAS 1C RAPPORT — ICKE-REFERERADE AVGÖRANDEN

**Datum:** 2026-02-22  
**Domstolar:** HDO, HFD  
**Typer:** DOM_ELLER_BESLUT, PROVNINGSTILLSTAND, NOTIS

---

## Resultat

**HDO (Högsta domstolen):**
- DOM_ELLER_BESLUT: 256 poster
- PROVNINGSTILLSTAND: 67 poster
- **Total HDO:** 323 poster

**HFD (Högsta förvaltningsdomstolen):**
- DOM_ELLER_BESLUT: 136 poster
- PROVNINGSTILLSTAND: 42 poster
- NOTIS: 47 poster
- **Total HFD:** 225 poster

**GRAND TOTAL:** 548 nya avgöranden

---

## Tekniska förbättringar

### 1. Nya filnamnsformat
```
HDO_2024_dom__mal-T123-24.json          # DOM_ELLER_BESLUT
HFD_2024_pt__mal-3020-24.json           # PROVNINGSTILLSTAND
HFD_2023_not-012__mal-4460-25.json      # NOTIS
```

### 2. Fallback-referatnummer
För avgöranden utan `referatNummerLista`:
- `"HFD 2024 dom 1"` (DOM_ELLER_BESLUT)
- `"HDO 2025 pt 3"` (PROVNINGSTILLSTAND)
- `"HFD 2023 not. 5"` (NOTIS)

Sekvensräknare per (domstol, år, typ).

### 3. PDF-extraktion för HDO DOM_ELLER_BESLUT
HDO DOM_ELLER_BESLUT saknar `innehall` (HTML).
Lösning: Hämta PDF via `/api/v1/bilagor/{fillagringId}` och extrahera text med pdfplumber.

---

## Kodändringar

**Nya filer:**
- `pdf_extractor.py` — PDF-hämtning och textextraktion

**Uppdaterade filer:**
- `naming.py` — Nya funktioner: `generate_filename_dom()`, `generate_filename_pt()`, `generate_filename_notis()`, `generate_filename_for_type()`
- `harvester.py` — Fallback-logik för tom `referatNummerLista`, PDF-berikning för HDO
- `cli.py` — Stöd för alla 5 avgörandetyper
- `test_fas1c.py` — 7 nya tester (totalt 97 passed)

---

## Verifiering
```bash
# HDO
find data/raw/HDO -name "*_dom__*.json" | wc -l    # 256
find data/raw/HDO -name "*_pt__*.json" | wc -l     # 67

# HFD
find data/raw/HFD -name "*_dom__*.json" | wc -l    # 136
find data/raw/HFD -name "*_pt__*.json" | wc -l     # 42
find data/raw/HFD -name "*_not-*.json" | wc -l     # 47
```

✅ Alla volymer matchar API-katalogen från Fas 0.

---

## Totalt harvested (alla faser)

| Domstol | REFERAT | DOM/BESLUT | PT | NOTIS | Total |
|---------|---------|------------|-----|-------|-------|
| **HDO** | 2,492 | 256 | 67 | 0 | 2,815 |
| **HFD** | 1,117 | 136 | 42 | 47 | 1,342 |
| **REGR** | 1,727 | — | — | — | 1,727 |
| **MIOD** | 350 | — | — | — | 350 |
| **TOTAL** | 5,686 | 392 | 109 | 47 | **6,234** |

---

## Nästa steg

- Fas 2 (fortsättning): Harvesta fler domstolar (ADO, HSV, MMOD, etc.)
- Fas 3: HTML-chunking med sektionsigenkänning
- Fas 4: RAG-pipeline

---

**Modell:** GPT-5.3-Codex (implementation)  
**Testresultat:** 97/97 passed  
**Diskutrymme:** +~50 MB
