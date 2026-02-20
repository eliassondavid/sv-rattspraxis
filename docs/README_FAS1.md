# FAS 1 — Generaliserad Harvester

## Mål
HFD-specifik harvesting har generaliserats till en domstolsagnostisk implementation för 22 svenska domstolar.

## Analys av `api_catalog.json`
- Katalogen innehåller 23 koder totalt.
- `DOV` (Domstolsverket) har 0 volym i alla typer och har därför exkluderats från körbar domstolskonfiguration.
- `COURTS` innehåller 22 domstolar med:
  - domstolskod
  - namn
  - volymer per typ
  - referatnummerformat
  - målnummerformat
  - prioritet
  - stöd för innehåll/bilagor

### Domstolskoder i `COURTS`
`ADO, HDO, HFD, HGO, HNN, HON, HSB, HSV, HVS, HYOD, KGG, KJO, KST, KSU, MDO, MIOD, MMOD, MOD, PBR, PMOD, REGR, RHN`

### Referatformat (exempel)
- `HFD`: `HFD YYYY ref. N`
- `REGR`: `RÅ YYYY ref. N`
- `ADO`: `AD YYYY nr N`
- `MIOD`: `MIG YYYY:N`
- `KST`: `RK YYYY:N`
- Hovrätter: `RH YYYY:N`
- Legacy/domstolar utan konsekvent referatnummer i katalogen: `Saknas`

### Målnummerformat (exempel)
- `NNNN-NN`
- `X NNNN-NN`
- `XX NNNNN-NN`
- `A NNN/NN`
- `YYYY-N`

## Implementerade ändringar

### 1. `src/sv_rattspraxis/courts.py` (ny/utökad)
- Ny `CourtConfig`-dataclass.
- Ny `COURTS`-dict för 22 domstolar.
- Ny hjälpfunktion `get_court_config()`.

### 2. `src/sv_rattspraxis/harvester.py` (refactor)
- Ny klass: `DomstolHarvester`.
- `domstol_kod` parametriseras i konstruktorn.
- Domstol valideras mot `COURTS`.
- Sökfilter använder vald domstol i `domstolKodLista`.
- Befintlig kärnlogik kvar:
  - paginering
  - rå JSON-lagring
  - SHA-256
  - masterlist-export
- Bakåtkompatibilitet via alias: `Harvester = DomstolHarvester`.

### 3. `src/sv_rattspraxis/naming.py` (refactor)
- Filnamn generaliserat från `HFD_...` till `{DOMSTOL}_...`.
- `generate_filename()` tar nu `domstol` som parameter.
- Parser för målnummer breddad för fler format (prefix/slash).
- `validate_filename()` uppdaterad för generell domstolsprefix.

### 4. `src/sv_rattspraxis/cli.py` (uppdaterad)
- `harvest` har `--court` med default `HFD`.
- Validering av domstol mot `COURTS`.
- Stöd för `--court ALL` för batch-körning av alla konfigurerade domstolar.

## Exempel
```bash
sv-rp harvest --court HFD --type REFERAT
sv-rp harvest --court HDO --type REFERAT --from-year 2020
sv-rp harvest --court ALL --type REFERAT --from-year 2024
```

## Bakåtkompatibilitet
- HFD fungerar fortsatt som default i CLI.
- Tidigare `Harvester`-namn stöds via alias till `DomstolHarvester`.
