# MALNUMMER_FORMAT.md

## Syfte
Detta dokument beskriver målnummerformat som stöds i `MalnummerParser` (Fas 1B), inklusive normaliseringsregler och verifiering med tester.

## Format per domstol

| Domstolskod | Domstol | Format (courts.py) | Exempel |
|---|---|---|---|
| ADO | Arbetsdomstolen | `A NNN/NN` | `A 153/24` |
| HDO | Högsta domstolen | `X NNNN-NN` | `Ö 6478-25` |
| HFD | Högsta förvaltningsdomstolen | `NNNN-NN` | `4460-25` |
| HGO | Göta hovrätt | `X NNNN-NN` | `B 2455-25` |
| HNN | Hovrätten för Nedre Norrland | `XX NNN-NN` | `ÖÄ 717-20` |
| HON | Hovrätten för Övre Norrland | `X NNN-NN` | `B 672-22` |
| HSB | Hovrätten över Skåne och Blekinge | `X NNNN-NN` | `B 5581-24` |
| HSV | Svea hovrätt | `X NNNNN-NN` | `K 13251-25` |
| HVS | Hovrätten för Västra Sverige | `X NNNN-NN` | `Ä 7634-24` |
| HYOD | Svea hovrätts hyresrättsliga avgöranden | `X NNNNN-NN` | `H 15144-24` |
| KGG | Kammarrätten i Göteborg | `NNN-NN` | `787-01` |
| KJO | Kammarrätten i Jönköping | `NNNN-NN` | `2622-05` |
| KST | Kammarrätten i Stockholm | `NNNN-NN` | `7433-21` |
| KSU | Kammarrätten i Sundsvall | `NNNN-NN` | `3546-00` |
| MDO | Marknadsdomstolen | `YYYY-N` | `2016-9` |
| MIOD | Migrationsöverdomstolen | `XX NNNNN-NN` | `UM 12369-24` |
| MMOD | Mark- och miljööverdomstolen | `M NNNNN-NN` | `M 11808-23` |
| MOD | Miljööverdomstolen | `M NNNN-NN` | `M 4256-10` |
| PBR | Patentbesvärsrätten | `NN-NNN` | `10-292` |
| PMOD | Patent- och marknadsöverdomstolen | `XXX NNNNN-NN` | `PMT 10755-25` |
| REGR | Regeringsrätten | `NNNN-NN` | `5486-09` |
| RHN | Rättshjälpsnämnden | `NN-NN` | `33-09` |

## HFD-specifika varianter som hanteras

- Single: `4033-09`
- Lista med komma: `6963-15, 6969-15`
- Lista med `och`/`samt`: `6980-24 och 6981-24`
- Intervall en-dash: `6107–6109-23`
- Intervall dubbel-dash: `6159--6160-14`
- Intervall enkel dash: `4569-4571-22`
- Kombinationer: `6578-14, 6159--6160-14`, `7550–7558-21 samt 664–669-22`

## Normaliseringsregler

1. Intervalltecken normaliseras: `–` och `—` -> `--`.
2. Listseparatorer normaliseras: `,`, `;`, `och`, `samt` -> tokenisering per målnummer.
3. Prefixtext i början tas bort: `Mål`, `Mål nr`, `Mål nr.`, `Mål:`.
4. Whitespace normaliseras i träffat målnummer: multipla blanksteg -> ett blanksteg.
5. Range-expansion görs för format `start<sep>end-år` där `<sep>` är `–`, `--` eller `-`.
6. Vid range med omvänd ordning (`end < start`) byts start/slut före expansion.
7. Om token inte matchar ett känt format returneras `None` från `parse_single` och token ignoreras i output.

## Regex-översikt

- Prefix + årsuffix: `[A-ZÅÄÖ]{1,6}\s*\d{1,6}-\d{2}`
- Prefix + slash-år: `[A-ZÅÄÖ]{1,6}\s*\d{1,6}/\d{2}`
- Standard numeriskt: `\d{1,6}-\d{2}`
- MDO-format: `\d{4}-\d{1,3}`
- PBR-kortformat: `\d{1,3}-\d{1,3}`
- Range: `\d{1,6}(--|–|-)\d{1,6}-\d{2}` (med tillåtna mellanrum)

## Testresultat

Kört lokalt i projektmappen:

```bash
pytest -q test_malnummer.py
```

Utfall:
- `57 passed`

Coverage:

```bash
pytest -q test_malnummer.py --cov=naming --cov-report=term
```

Utfall:
- `naming.py: 100%`
- `TOTAL: 100%`
