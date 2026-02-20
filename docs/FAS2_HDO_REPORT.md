# FAS 2 RAPPORT — HDO HARVESTING

**Datum:** 2026-02-20  
**Domstol:** HDO (Högsta domstolen)  
**Typ:** REFERAT  
**Körning:** Fas 2 - Metadata-normalisering

---

## Resultat

- **Totalt referat:** 2,492
- **Tidsperiod:** 2000-2025
- **Diskutrymme:** 84 MB
- **Målnummerparsning:** 100% success (0 UNKNOWN)

---

## Fördelning per år (topp 10)

| År | Antal referat |
|----|---------------|
| 2007 | 124 |
| 2001 | 124 |
| 2013 | 113 |
| 2008 | 112 |
| 2017 | 109 |
| 2000 | 108 |
| 2016 | 104 |
| 2005 | 102 |
| 2004 | 102 |
| 2021 | 101 |

---

## Teknisk verifiering

✅ **Filstruktur:**
```
data/raw/HDO/           2,492 JSON-filer
data/processed/HDO/     masterlist.csv (2,493 rader)
docs/samples/HDO/       3 exempel-filer
```

✅ **Målnummerparsning:**
- 100% framgång
- Format: T NNNN-NN, B NNNN-NN, Ö NNNN-NN, P NNNN-NN, etc.
- Alla prefix korrekt hanterade

✅ **Referatnummerformat:**
- NJA YYYY s. N (standardformat för HDO)
- Exempel: "NJA 2024 s. 1", "NJA 2000 s. 3"

✅ **SHA-256 hashes:**
- Alla filer har verifierad integritet

---

## API-detaljer

- **Endpoint:** https://rattspraxis.etjanst.domstol.se/api/v1/sok
- **Rate limiting:** 1.5s mellan anrop
- **Körning:** ~2 minuter (API hanterade 25 sidor)
- **Inga 429-fel** (rate limit respekterat)

---

## Noteringar

**Färre än förväntat:**
- API-katalogen (Fas 0) rapporterade 5,518 totalt för HDO
- Vi fick 2,492 REFERAT från 2000-2025
- Skillnaden beror troligen på:
  - DOM_ELLER_BESLUT (256 poster) ej inkluderade
  - PROVNINGSTILLSTAND (67 poster) ej inkluderade
  - Äldre referat före 2000
  - Andra avgörandetyper

**Nästa steg:**
- Fas 1c: Harvesta DOM_ELLER_BESLUT + PROVNINGSTILLSTAND för HDO
- Fas 2 (forts): REGR (1,727 referat), MIOD (526), etc.

---

## Sample-filer

Se `docs/samples/HDO/` för exempel:
- HDO_2024_ref-001__mal-P124-23.json
- HDO_2024_ref-010__mal-*.json
- HDO_2000_ref-001__mal-*.json

**OBS:** Rå data (2,492 filer, 84 MB) lagras lokalt i `data/raw/HDO/` och är exkluderad från Git via `.gitignore`.
