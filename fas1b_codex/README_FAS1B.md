# README_FAS1B.md

## Fas 1B: Robust målnummerparsning

Denna leverans uppdaterar parsern för målnummer så att den robust hanterar HFD-varianter och format från samtliga domstolstyper i `courts.py`/`api_catalog.json`.

## Levererade filer

1. `naming.py` (uppdaterad)
2. `test_malnummer.py` (ny)
3. `MALNUMMER_FORMAT.md` (ny)
4. `README_FAS1B.md` (denna fil)

## Ändringar i naming.py

- Utökat stöd för prefix i målnummer (upp till 6 bokstäver, inkl. svenska tecken), t.ex. `UM`, `PMT`, `PMÄ`, `ÖÄ`.
- Behåller och normaliserar prefix med whitespace, t.ex. `T   1234-22` -> `T 1234-22`.
- Förbättrad listsplit på `,`, `;`, `och`, `samt` (case-insensitivt).
- Robustare borttagning av inledande `Mål`/`Mål nr`/`Mål:`-prefix.
- Range-parser som hanterar `–`, `--` och `-` samt mellanrum kring separators.
- Range-expansion swappar automatiskt start/slut vid omvänd ordning.
- `parse_single` returnerar nu strikt `None` vid icke-match i stället för generell sifferfallback.
- Tillagt stöd för kort numeriskt format `NN-NNN` (PBR), utöver befintliga format.

## Testsvit

Ny fil `test_malnummer.py` innehåller 57 tester:

- HFD: single, listor, intervall, kombinationer
- HD/hovrätter: prefix (T/B/Ö/ÖÄ/Ä/K)
- AD: slash-format
- MOD/MMOD/MIOD/PMOD: M/UM/PMT/PMÄ
- MDO: `YYYY-N`
- PBR/RHN: kortformat `NN-NNN`/`NN-NN`
- Edge cases: tom input, ogiltiga tokens, `None`, direktmetoder för parse/split/range
- Hjälpfunktioner: `sanitize_malnummer_for_filename`, `generate_filename`, `parse_referat_nummer`, `validate_filename`

## Körda kommandon och utfall

```bash
pytest -q test_malnummer.py
```

- Resultat: `57 passed`

```bash
pytest -q test_malnummer.py --cov=naming --cov-report=term
```

- Resultat: `naming.py 100%` coverage

## Noteringar

- Parsern är nu striktare vid ogiltiga tokenformat, vilket minskar risken att skräpdata slinker igenom.
- Exempelsträngen `A samt B` hanteras i split-logik, men parsas inte som målnummer eftersom den saknar giltigt nummermönster.
