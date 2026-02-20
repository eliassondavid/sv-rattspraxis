# FAS 1 — CODEX WORKFLOW

## Filer att ladda upp till ChatGPT (GPT-5.3-Codex)

1. **FAS_1_INSTRUKTIONER.md** — Detaljerad guide
2. **PROMPT.txt** — Prompt att copy-paste
3. **api_catalog.json** — Fas 0-resultat
4. **harvester.py** — Befintlig HFD-harvester
5. **naming.py** — Filnamnskonvention
6. **cli.py** — CLI
7. **models.py** — Pydantic-modeller (referens)

## Workflow

### STEG 1: Öppna ChatGPT
- Gå till chat.openai.com
- Välj **GPT-5.3-Codex** (kodningsmodellen)
- Ny chat: "Fas 1 — Generalisera sv-rattspraxis harvester"

### STEG 2: Ladda upp 7 filer
Se listan ovan.

### STEG 3: Kör prompt
Copy-paste innehållet från **PROMPT.txt**

### STEG 4: Vänta
GPT-Codex arbetar i 10-30 minuter

### STEG 5: Ladda ner resultat
GPT-Codex levererar 5 filer:
- courts.py
- harvester.py (uppdaterad)
- naming.py (uppdaterad)
- cli.py (uppdaterad)
- README_FAS1.md

### STEG 6: Testa lokalt (med Claude)
```bash
# Kopiera filerna till src/sv_rattspraxis/
# Kör tester
make test

# Testa HFD (ska fortfarande fungera)
sv-rp harvest --court HFD

# Om allt OK → committa
```

### STEG 7: Committa (efter Claude-granskning)
Claude granskar alla ändringar innan push.
