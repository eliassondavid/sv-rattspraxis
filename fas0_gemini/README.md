# FAS 0 — GEMINI WORKFLOW

## Filer

1. **FAS_0_INSTRUKTIONER.md** — Detaljerad guide
2. **api_catalog_template.json** — Output-struktur
3. **models.py** — Pydantic-modeller
4. **PROMPT.txt** — Prompt att copy-paste till Gemini

## Workflow

### STEG 1: Öppna Gemini
- Gå till gemini.google.com
- Välj **Gemini 3.1 Pro** (kodningsmodellen)
- Ny chat: "Fas 0 — API-katalogisering"

### STEG 2: Ladda upp filer
Dra dessa 3 filer till Gemini-chatten:
1. FAS_0_INSTRUKTIONER.md
2. api_catalog_template.json
3. models.py

### STEG 3: Kör prompt
Copy-paste innehållet från **PROMPT.txt**

### STEG 4: Vänta
Gemini kör i 10-15 minuter

### STEG 5: Ladda ner resultat
Gemini skapar:
- api_catalog.json
- api_behavior_report.md
- edge_cases.md

### STEG 6: Committa till GitHub
```bash
cd /Users/davideliasson/Projects/sv-rattspraxis
mkdir -p data/catalog
mv ~/Downloads/api_catalog.json data/catalog/
mv ~/Downloads/api_behavior_report.md docs/
mv ~/Downloads/edge_cases.md docs/

git checkout develop
git add data/catalog/ docs/
git commit -m "feat(fas0): complete API cataloging for 22 courts"
git push
```

## Förväntad output

- **22 domstolar** katalogiserade
- **Volymmatris** (22 × 5 = 110 kombinationer)
- **Fältstruktur** per domstol
- **Edge cases** dokumenterade
- **Redo för Fas 1**
