# KOMPLETT HARVESTING-RAPPORT

**Datum:** 2026-02-22  
**Faser:** 0, 1, 1b, 1c, 2  
**Total:** 16,647 avgöranden från 20 domstolar

---

## Resultat per domstol

| Domstol | Referat | Dom/Beslut | PT | Notis | **Total** |
|---------|---------|------------|-----|-------|-----------|
| **HDO** | 5,195 | 256 | 67 | 0 | **5,518** |
| **HFD** | 1,342 | 0 | 0 | 0 | **1,342** |
| **REGR** | 1,727 | 0 | 0 | 0 | **1,727** |
| **ADO** | 1,977 | 0 | 0 | 0 | **1,977** |
| **MMOD** | 685 | 0 | 0 | 0 | **685** |
| **MOD** | 709 | 0 | 0 | 0 | **709** |
| **HSV** | 1,356 | 0 | 0 | 0 | **1,356** |
| **HVS** | 625 | 0 | 0 | 0 | **625** |
| **HSB** | 498 | 0 | 0 | 0 | **498** |
| **HGO** | 431 | 0 | 0 | 0 | **431** |
| **HNN** | 196 | 0 | 0 | 0 | **196** |
| **HON** | 166 | 0 | 0 | 0 | **166** |
| **HYOD** | 238 | 0 | 0 | 0 | **238** |
| **MIOD** | 526 | 0 | 0 | 0 | **526** |
| **PMOD** | 198 | 0 | 0 | 0 | **198** |
| **MDO** | 346 | 0 | 0 | 0 | **346** |
| **KST** | 75 | 0 | 0 | 0 | **75** |
| **KGG** | 8 | 0 | 0 | 0 | **8** |
| **KJO** | 23 | 0 | 0 | 0 | **23** |
| **KSU** | 3 | 0 | 0 | 0 | **3** |
| | | | | | |
| **TOTALT** | **16,324** | **256** | **67** | **0** | **16,647** |

**Diskutrymme:** 503 MB

---

## Coverage vs API-katalog (Fas 0)

| Domstol | Harvested | API-förväntat | Täckning |
|---------|-----------|---------------|----------|
| HDO | 5,518 | 5,518 | 100% ✓ |
| ADO | 1,977 | 1,979 | 99.9% ✓ |
| REGR | 1,727 | 1,727 | 100% ✓ |
| HSV | 1,356 | 1,374 | 98.7% ✓ |
| HFD | 1,342 | 1,342 | 100% ✓ |
| MMOD | 685 | 1,069 | 64.1% |
| MOD | 709 | 709 | 100% ✓ |

**Not:** Lägre coverage för MMOD beror troligen på filtrering (typ/tidsperiod).

---

## Teknisk sammanfattning

- **Modeller:** Gemini 3.1 Pro (Fas 0), Sonnet 4.5 (Fas 1/2), Opus 4.6 (Fas 1b), GPT-5.3-Codex (Fas 1c)
- **Tidsperioder:** 1981-2026 (HDO), 1990-2026 (andra domstolar)
- **Typer:** REFERAT, DOM_ELLER_BESLUT, PROVNINGSTILLSTAND, NOTIS
- **PDF-extraktion:** Fungerar för HDO DOM_ELLER_BESLUT
- **Målnummerparsning:** 100% framgång (0 UNKNOWN)
- **Tester:** 97/97 passed

---

## Nästa fas

**Fas 3 — HTML-chunking:**
- Parsa `innehall`-HTML till strukturerad text
- Sektionsigenkänning (BAKGRUND, DOMSKÄL, DOMSLUT)
- Bevara styckenumrering för pinpoints
- Lagrum-kontext per chunk

**Modell:** Opus 4.6 + Extended Thinking  
**Tid:** 3-5 timmar
