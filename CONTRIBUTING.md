# Bidragsriktlinjer

Tack för ditt intresse att bidra till sv-rattspraxis! 🎉

---

## 🤝 Hur du kan bidra

### 1. Rapportera buggar

Använd GitHub Issues med [bug report-mallen](.github/ISSUE_TEMPLATE/bug_report.md).

**Inkludera:**
- Steg för att återskapa
- Förväntat vs. faktiskt beteende
- Loggutdrag
- Miljöinfo (OS, Python-version, sv-rattspraxis version)

### 2. Föreslå nya funktioner

Använd GitHub Issues med [feature request-mallen](.github/ISSUE_TEMPLATE/feature_request.md).

**Inkludera:**
- Användningsfall
- Alternativ du har övervägt
- Påverkan (slutanvändare, utvecklare, forskare)

### 3. Bidra med kod

1. **Forka repot**
2. **Skapa en feature branch:** `git checkout -b feature/min-funktion`
3. **Gör dina ändringar**
4. **Kör tester:** `make test`
5. **Kör linting:** `make lint`
6. **Commita:** `git commit -m "Add: beskrivning av ändring"`
7. **Pusha:** `git push origin feature/min-funktion`
8. **Öppna en Pull Request**

---

## 📝 Kodstandarder

### Python-stil

- Python 3.11+
- Type hints obligatoriska
- Docstrings på svenska (för offentliga funktioner)
- ruff för linting och formatering
- mypy för type checking

**Exempel:**

```python
def harvest_court(court: DomstolKod, type: PubliceringsTyp) -> list[Publikation]:
    """
    Harvesta publikationer från en domstol.
    
    Args:
        court: Domstolskod (t.ex. HFD, HDO)
        type: Publikationstyp (t.ex. REFERAT)
    
    Returns:
        Lista med publikationer
    
    Raises:
        APIError: Om API-anrop misslyckas
    """
    ...
```

### Commit-meddelanden

Följ [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: lägg till stöd för målnummerparsning
fix: korrigera filnamnskonvention för HDO
docs: uppdatera API-referens med ny endpoint
test: lägg till testfall för sekvenskontroll
refactor: generalisera harvester-logik
```

### Branch-naming

```
feature/beskrivning     # Ny funktion
fix/beskrivning         # Buggfix
docs/beskrivning        # Dokumentation
refactor/beskrivning    # Refaktorisering
test/beskrivning        # Tester
```

---

## 🧪 Tester

### Kör alla tester

```bash
make test
```

### Kör specifikt test

```bash
pytest tests/test_malnummer.py -v
```

### Täckningsgrad

Vi strävar efter ≥80 % coverage på kärnmoduler.

```bash
pytest --cov=sv_rattspraxis --cov-report=html
```

### Teststruktur

```
tests/
├── conftest.py              # Fixtures
├── test_api_client.py       # API-klient
├── test_malnummer.py        # Målnummerparsning
├── test_naming.py           # Filnamnskonvention
├── test_verify.py           # Integritetskontroll
└── fixtures/
    ├── sample_hfd_response.json
    └── sample_malnummer.json
```

---

## 📚 Dokumentation

### Uppdatera README

Om du lägger till ny funktionalitet, uppdatera README.md med:
- Exempel på användning
- CLI-kommandon
- Relevanta länkar

### API-dokumentation

Uppdatera `docs/API_REFERENCE.md` om du:
- Lägger till nytt endpoint
- Ändrar request/response-format
- Upptäcker nya beteendeavvikelser

### Docstrings

Alla offentliga funktioner och klasser ska ha docstrings:

```python
def parse_malnummer(text: str) -> list[MalNummer]:
    """
    Parsa målnummer från text.
    
    Stödjer:
    - Single: "1234-22"
    - Lista: "1234-22, 1235-22"
    - Intervall: "1234-1236-22"
    - Kombinationer: "1234-22 och 1235-1237-23"
    
    Args:
        text: Text med målnummer
    
    Returns:
        Lista med parsade målnummer
    
    Raises:
        ValueError: Om målnummer inte kan parsas
    
    Exempel:
        >>> parse_malnummer("1234-22")
        [MalNummer(nummer=1234, ar=22)]
        
        >>> parse_malnummer("1234-1236-22")
        [MalNummer(nummer=1234, ar=22), 
         MalNummer(nummer=1235, ar=22),
         MalNummer(nummer=1236, ar=22)]
    """
```

---

## 🔍 Code Review-process

### Vad vi letar efter

1. **Funktionalitet:** Löser koden problemet?
2. **Tester:** Finns det tester? Täcker de edge cases?
3. **Dokumentation:** Är dokumentationen uppdaterad?
4. **Kodkvalitet:** Följer koden våra standarder?
5. **Prestanda:** Finns det uppenbara flaskhalsar?

### Feedback

- Var konstruktiv och respektfull
- Förklara *varför* du föreslår en ändring
- Föreslå lösningar, inte bara problem

---

## 🎯 Prioriterade områden

### Hög prioritet

1. **Fas 0:** API-katalogisering (Gemini)
2. **Fas 1:** Generaliserad harvester
3. **Fas 1b:** Målnummerparsning
4. **Tester:** Öka coverage till 80 %+

### Medel prioritet

1. **Fas 2:** Metadata-normalisering
2. **PDF-pipeline:** För DOM_ELLER_BESLUT
3. **Inkrementell uppdatering:** Schemalagd harvesting

### Låg prioritet (men välkommet!)

1. **Fas 3:** HTML-chunking
2. **Fas 4:** RAG-pipeline
3. **Doktrin-katalog:** Extrahera litteratur

---

## 📋 Checklista för Pull Requests

- [ ] Kod följer projektets stilguide (ruff + mypy pass)
- [ ] Tester tillagda/uppdaterade
- [ ] Dokumentation uppdaterad
- [ ] CHANGELOG.md uppdaterad
- [ ] Commit-meddelanden följer konvention
- [ ] Alla tester passerar lokalt
- [ ] PR-beskrivning förklarar ändringarna

---

## ❓ Frågor?

- **GitHub Issues:** https://github.com/eliassondavid/sv-rattspraxis/issues
- **Diskussioner:** https://github.com/eliassondavid/sv-rattspraxis/discussions

---

## 📜 Code of Conduct

Vi följer [Contributor Covenant](https://www.contributor-covenant.org/):

- Var respektfull
- Var inkluderande
- Var professionell
- Fokusera på vad som är bäst för projektet

---

**Tack för ditt bidrag! 🙏**
