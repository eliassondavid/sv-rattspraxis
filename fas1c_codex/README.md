# FAS 1C — CODEX WORKFLOW

## Filer att ladda upp
1. FAS_1C_INSTRUKTIONER.md
2. PROMPT.txt
3. naming.py
4. harvester.py
5. api_catalog.json

## Workflow
1. Öppna ChatGPT → GPT-5.3-Codex
2. Ladda upp filer
3. Copy-paste PROMPT.txt
4. Vänta på resultat
5. Testa lokalt
6. Committa

## Efter Codex
```bash
# Kopiera filer
cp naming.py src/sv_rattspraxis/
cp harvester.py src/sv_rattspraxis/
cp pdf_extractor.py src/sv_rattspraxis/
cp test_fas1c.py tests/

# Installera PDF-bibliotek
pip install pdfplumber

# Testa
make test

# Harvesta
sv-rp harvest --court HDO --type DOM_ELLER_BESLUT
sv-rp harvest --court HDO --type PROVNINGSTILLSTAND
sv-rp harvest --court HFD --type DOM_ELLER_BESLUT
sv-rp harvest --court HFD --type PROVNINGSTILLSTAND
sv-rp harvest --court HFD --type NOTIS
```
