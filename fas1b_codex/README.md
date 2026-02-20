# FAS 1B — CODEX WORKFLOW

## Filer att ladda upp till ChatGPT (GPT-5.3-Codex)

1. **FAS_1B_INSTRUKTIONER.md** — Detaljerad guide
2. **PROMPT.txt** — Prompt att copy-paste
3. **HFD-mal_nr.md** — HFD-varianter
4. **naming.py** — Befintlig parser
5. **courts.py** — Format per domstol
6. **api_catalog.json** — Edge cases (referens)

## Workflow

### STEG 1: Öppna ChatGPT
- Gå till chat.openai.com
- Välj **GPT-5.3-Codex**
- Samma projekt som Fas 1 ELLER ny chat

### STEG 2: Ladda upp 6 filer
Se listan ovan.

### STEG 3: Kör prompt
Copy-paste innehållet från **PROMPT.txt**

### STEG 4: Vänta
GPT-Codex arbetar i 10-30 minuter

### STEG 5: Ladda ner resultat
GPT-Codex levererar 4 filer:
- naming.py (uppdaterad)
- test_malnummer.py (ny)
- MALNUMMER_FORMAT.md (ny)
- README_FAS1B.md

### STEG 6: Testa lokalt (med Claude)
```bash
# Kopiera filerna
cp naming.py src/sv_rattspraxis/
cp test_malnummer.py tests/
cp MALNUMMER_FORMAT.md docs/
cp README_FAS1B.md docs/

# Kör tester
pytest tests/test_malnummer.py -v
make test

# Om allt OK → committa
```

### STEG 7: Committa (efter Claude-granskning)
Claude granskar alla ändringar innan push.
