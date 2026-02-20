# sv-rattspraxis

**Harvester & RAG-pipeline för svensk rättspraxis**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 Översikt

`sv-rattspraxis` är en öppen källkods-pipeline för programmatisk inhämtning, strukturering och RAG-förberedelse av **all publicerad svensk rättspraxis** via Domstolsverkets REST-API.

**Omfattning:** 22 domstolar, ~17 000 avgöranden  
**Datakälla:** `rattspraxis.etjanst.domstol.se/api/v1/` (öppet API)  
**Status:** HFD klar (1 117 referat), generalisering pågår

---

## 🎯 Syfte

### Problem
- Manuellt PDF-letande i fragmenterade databaser
- Ingen strukturerad metadata för bulk-analys
- Bristande verifierbarhet i AI-genererade rättskällor

### Lösning
- Programmatisk tillgång till 17 000+ avgöranden
- Strukturerad metadata (JSON)
- Fulltext-HTML med bevarade citat
- Anti-hallucination via masterlist-verifiering
- Prejudikatsökning med pinpoints

### Användningsområden
- AI-stödd rättslig argumentation (Överklagande-skill v2.0+)
- Rättsvetenskaplig forskning
- Citatanalys och rättsutveckling
- Access to justice-initiativ

---

## 🚀 Quickstart

### Installation

```bash
# Klona repo
git clone git@github.com:eliassondavid/sv-rattspraxis.git
cd sv-rattspraxis

# Installera (Python 3.11+)
pip install -e .

# För utveckling
pip install -e ".[dev]"
```

### Godkänn upstream-villkor

```bash
sv-rp init --accept-terms
```

Detta skapar `.sv-rp-terms-accepted` och bekräftar att du förstår:
- Data omfattas av Offentlighetsprincipen (TF 2:1)
- Domstolsverket äger ej upphovsrätt till avgöranden
- Respektfull API-användning (≥1.5s mellan anrop)

### Harvesta rättspraxis

```bash
# En domstol
sv-rp harvest --court HFD --type referat

# Flera domstolar
sv-rp harvest --court HDO,REGR --type referat

# Alla domstolar (använd med försiktighet)
sv-rp harvest --court ALL --type referat
```

### Verifiera integritet

```bash
sv-rp verify
```

### Exportera masterlist

```bash
# CSV per domstol
sv-rp export --format csv --output data/masterlist/

# JSON (alla domstolar)
sv-rp export --format json --output data/masterlist/ALL_masterlist.json
```

---

## 📊 Domstolar och volymer

| Kod | Domstol | Publikationer | Status |
|-----|---------|---------------|--------|
| HDO | Högsta domstolen | 5 518 | Planerad (Fas 1) |
| ADO | Arbetsdomstolen | 1 979 | Planerad (Fas 2) |
| REGR | Regeringsrätten (–2010) | 1 727 | Planerad (Fas 1) |
| HFD | Högsta förvaltningsdomstolen | 1 342 | ✅ Klar |
| ... | *(18 domstolar till)* | 8 782 | Planerad |
| **TOTALT** | **22 domstolar** | **17 348** | |

Se [MASTER_PLAN.md](docs/MASTER_PLAN.md) för komplett lista.

---

## 🏗️ Arkitektur

```
sv-rattspraxis/
├── src/sv_rattspraxis/     # Källkod
│   ├── cli.py              # CLI: sv-rp
│   ├── api_client.py       # REST-klient
│   ├── harvester.py        # Paginerad inhämtning
│   ├── naming.py           # Filnamnskonvention
│   ├── malnummer.py        # Målnummerparsning
│   ├── verify.py           # Integritetskontroll
│   └── courts.py           # Domstolskonfiguration
├── data/                   # ⚠️ .gitignore
│   ├── raw/                # Rå API-svar
│   ├── processed/          # Normaliserad metadata
│   ├── masterlist/         # Masterlists (CSV/JSON)
│   └── logs/
├── docs/                   # Dokumentation
└── tests/                  # Testsvit
```

---

## 📚 Dokumentation

- **[MASTER_PLAN.md](docs/MASTER_PLAN.md)** — Komplett projektplan (Fas 0–4)
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** — API-dokumentation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Systemarkitektur
- **[UPSTREAM_SOURCES.md](docs/UPSTREAM_SOURCES.md)** — Datakällor och attribution
- **[DATA_POLICY.md](docs/DATA_POLICY.md)** — Personuppgifter, RAG-policy

---

## 🔬 Kvalitetssäkring

### Anti-hallucination

Varje referens som AI:n genererar kan verifieras mot masterlist:

```python
from sv_rattspraxis.verify import verify_source_authenticity

verify_source_authenticity("HFD 2022 ref. 10")  # True
verify_source_authenticity("HFD 2099 ref. 1")   # False (existerar ej)
```

### Citatformat per domstol

| Domstol | Format | Exempel |
|---------|--------|---------|
| HFD | `HFD {YYYY} ref. {N}` | HFD 2023 ref. 42 |
| HD | `NJA {YYYY} s. {N}` | NJA 2023 s. 374 |
| RÅ | `RÅ {YYYY} ref. {N}` | RÅ 2010 ref. 8 |
| AD | `AD {YYYY} nr {N}` | AD 2022 nr 45 |

### Sekvenskontroll

```bash
sv-rp verify
```

Kontrollerar:
- Ref 1→N per år (flagga luckor)
- SHA-256 integritet
- Målnummerparsning
- Fil-metadata konsistens

---

## 🛠️ Utveckling

### Kör tester

```bash
make test
```

### Linting

```bash
make lint
```

### Harvesta (development)

```bash
# Med debug-logging
sv-rp harvest --court HFD --type referat --log-level DEBUG
```

---

## 📖 Citering

Om du använder denna pipeline i akademisk forskning, vänligen citera:

```bibtex
@software{sv_rattspraxis,
  author = {Eliasson, David},
  title = {sv-rattspraxis: Harvester \& RAG-pipeline för svensk rättspraxis},
  year = {2026},
  url = {https://github.com/eliassondavid/sv-rattspraxis}
}
```

---

## 📜 Licens

**Kod:** [Apache License 2.0](LICENSE)

- **Kräver attribution:** David Eliasson måste nämnas som upphovsman
- **NOTICE-fil:** Måste bevaras vid distribution
- **Ändringar:** Måste dokumenteras

**Data:**

- **Rättspraxis** (data/): Offentlig handling under Offentlighetsprincipen (TF 2:1)  
  Domstolsverket äger ej upphovsrätt till rättsliga avgöranden.

- **Juridikbok.se-innehåll** (framtida integration):  
  Icke-kommersiell användning, attribution krävs.  
  Se [JURIDIKBOK_LICENSE.md](docs/JURIDIKBOK_LICENSE.md) för detaljer.

Se [UPSTREAM_TERMS.md](docs/UPSTREAM_TERMS.md) för fullständig information.

---

## 🤝 Bidrag

Se [CONTRIBUTING.md](CONTRIBUTING.md) för guidelines.

**Områden där bidrag välkomnas:**
- Stöd för fler domstolar
- OCR-pipeline för äldre avgöranden
- Doktrincitat-extraktion
- Utländsk rättspraxis (HUDOC, CURIA)

---

## 🔗 Relaterade projekt

- **[Överklagande-skill v2.0](docs/PRODUKTVISION.md)** — AI-stödd rättslig argumentation
- **riksdag-sfs** (planerad) — Harvester för SFS + förarbeten
- **sv-rattskallor-schema** (planerad) — Universellt Source-schema

---

## 📧 Kontakt

**Projekt:** https://github.com/eliassondavid/sv-rattspraxis  
**Issues:** https://github.com/eliassondavid/sv-rattspraxis/issues  
**Författare:** David Eliasson

---

**OBS:** Detta är forsknings- och utvecklingsprojekt. För produktionsanvändning, 
kontakta författaren.
