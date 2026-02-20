# Changelog

Alla noterbara ändringar i detta projekt dokumenteras i denna fil.

Formatet baseras på [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
och projektet följer [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planerat
- Fas 1: Generaliserad harvester för alla 22 domstolar
- Fas 1b: Målnummerparsning
- Fas 2: Metadata-normalisering

## [0.1.0] - 2026-02-19

### Tillagt
- Initial projektstruktur
- README med översikt och quickstart
- Licens (MIT för kod)
- .gitignore för Python och data
- pyproject.toml med beroenden
- Makefile med vanliga kommandon
- CITATION.cff för akademisk citering
- Grundläggande dokumentation

### Status
- HFD-harvester färdig (1 117 referat)
- Befintlig kod redo att migreras till ny struktur

## [0.0.1] - 2026-01-XX (HFD-endast)

### Tillagt
- HFD-specifik harvester
- API-klient mot Domstolsverkets REST-API
- Filnamnskonvention
- SHA-256 integritetskontroll
- Sekvensvalidering

---

## Versionsschema

| Version | Fas | Innehåll |
|---------|-----|----------|
| 0.1.0 | Initial | Projektstruktur, HFD klar |
| 0.2.0 | Fas 0 | API-katalog (api_catalog.json) |
| 1.0.0 | Fas 1 | HFD + HDO + REGR harvested, generaliserad harvester |
| 1.1.0 | Fas 1b | Målnummerparsning |
| 2.0.0 | Fas 2 | Metadata normaliserad, alla domstolar |
| 3.0.0 | Fas 3 | Chunking med sektioner |
| 4.0.0 | Fas 4 | RAG-pipeline |
