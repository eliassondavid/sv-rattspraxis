# FAS 1C — ICKE-REFERERADE AVGÖRANDEN

**Syfte:** Harvesta alla avgöranden från HD/HFD som INTE är referat  
**Modell:** GPT-5.3-Codex  
**Tidsuppskattning:** 1-2 timmar kodning + 30 min harvesting

---

## UPPGIFTER

### 1. Nya avgörandetyper att harvesta

**HDO (Högsta domstolen):**
- DOM_ELLER_BESLUT: 256 poster
- PROVNINGSTILLSTAND: 67 poster  
- NOTIS: 0 (inga notiser i API:t för HDO)

**HFD (Högsta förvaltningsdomstolen):**
- DOM_ELLER_BESLUT: 136 poster
- PROVNINGSTILLSTAND: 42 poster
- NOTIS: 47 poster

**Total:** 548 nya avgöranden

---

## TEKNISKA SKILLNADER

| Fält | REFERAT | DOM_ELLER_BESLUT | PROVNINGSTILLSTAND | NOTIS |
|------|---------|------------------|--------------------|-------|
| `innehall` (HTML) | ✅ Alltid | HDO: ❌ / HFD: ✅ | ❌ | ✅ |
| `bilagaLista` (PDF) | Sällan | HDO: ✅ / HFD: ✅ | Sällan | Sällan |
| `referatNummerLista` | ✅ Ifylld | ❌ Tom [] | ❌ Tom [] | ✅ Ifylld |
| `sammanfattning` | ✅ | ✅ | ✅ (kort) | ✅ |
| `benamning` | Ej vanligt | HDO: ✅ | HDO: ✅ | Ej vanligt |

---

## KODÄNDRINGAR BEHÖVS

### 1. Filnamnskonvention (naming.py)

**Nuvarande:**
```
{DOMSTOL}_{YEAR}_ref-{NNN}__mal-{MALNR}.json
```

**Nytt:**
```
{DOMSTOL}_{YEAR}_dom__mal-{MALNR}.json          # DOM_ELLER_BESLUT
{DOMSTOL}_{YEAR}_pt__mal-{MALNR}.json           # PROVNINGSTILLSTAND
{DOMSTOL}_{YEAR}_not-{NNN}__mal-{MALNR}.json   # NOTIS
```

### 2. Harvester-logik (harvester.py)

**Problem:** DOM_ELLER_BESLUT och PT har tom `referatNummerLista`

**Lösning:** Fallback-strategi för posts utan referat:
- Använd `avgorandedatum` för år
- Generera sekventiell `ref_no` per typ och år
- Format: `HDO 2024 dom 1`, `HFD 2024 pt 5`, `HFD 2023 not. 12`

### 3. PDF-hantering (ny modul: pdf_extractor.py)

**HDO DOM_ELLER_BESLUT saknar `innehall`** → PDF måste extraheras
```python
async def extract_pdf_from_bilaga(bilaga_id: str) -> str:
    """Hämta PDF via /api/v1/bilagor/{fillagringId} och extrahera text."""
    url = f"{base_url}/bilagor/{bilaga_id}"
    response = await client.get(url)
    pdf_bytes = response.content
    
    # Använd pdfplumber eller PyMuPDF
    import pdfplumber
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)
    
    return text
```

---

## LEVERABLER

1. **naming.py** (uppdaterad) — Nya filnamnsformat
2. **harvester.py** (uppdaterad) — Hantera tomma referatNummerLista
3. **pdf_extractor.py** (ny) — Extrahera text från PDFs
4. **test_fas1c.py** (ny) — Tester för nya typer
5. **README_FAS1C.md** — Dokumentation

---

## VERIFIERING

Efter harvesting:
```bash
# HDO
find data/raw/HDO -name "*_dom__*.json" | wc -l    # Förväntat: 256
find data/raw/HDO -name "*_pt__*.json" | wc -l     # Förväntat: 67

# HFD
find data/raw/HFD -name "*_dom__*.json" | wc -l    # Förväntat: 136
find data/raw/HFD -name "*_pt__*.json" | wc -l     # Förväntat: 42
find data/raw/HFD -name "*_not-*.json" | wc -l     # Förväntat: 47
```

---

## KVALITETSKRAV

✅ Alla typer harvestade  
✅ PDF-extraktion fungerar för HDO DOM_ELLER_BESLUT  
✅ Filnamn följer ny konvention  
✅ Sekvenskontroll per typ  
✅ Tester passar
