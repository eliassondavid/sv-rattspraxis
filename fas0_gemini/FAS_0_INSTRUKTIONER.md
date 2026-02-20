# FAS 0 — API-KATALOGISERING

**Modell:** Gemini 3.1 Pro  
**Tidsuppskattning:** 10-15 minuter  
**Rate limit:** 1.5 sekunder mellan API-anrop

---

## UPPDRAG

Kartlägga Domstolsverkets REST-API för svensk rättspraxis.

**API:** `https://rattspraxis.etjanst.domstol.se/api/v1/`  
**Autentisering:** Ingen (öppet API)

---

## UPPGIFTER

### 1. Hämta domstolslista
GET `/api/v1/domstolar`

Förväntat: 22 domstolar

### 2. Hämta volymer per domstol
POST `/api/v1/sokforfiningar` för varje domstol × typ

Typer: REFERAT, NOTIS, DOM_ELLER_BESLUT, PROVNINGSTILLSTAND, FORHANDSAVGORANDE

### 3. Hämta exempelposter
POST `/api/v1/sok` — 5 referat per domstol

Verifiera:
- `innehall` finns (fulltext HTML)
- `referatNummerLista` format
- `malNummerLista` format
- `litteraturLista` finns?
- `bilagaLista` finns?
- `europarattsligaAvgorandenLista` finns?

### 4. Testa paginering
För 5 största domstolarna (HDO, ADO, REGR, HSV, HFD):
- Hämta sida 0
- Hämta sida 1
- Verifiera ingen överlapp

---

## RATE LIMITING (KRITISKT!)

Vänta 1.5 sekunder mellan VARJE API-anrop.

User-Agent: `SVRattspraxisHarvester/1.0 (Fas 0 Cataloging)`

---

## OUTPUT

1. `api_catalog.json` — Strukturerad data
2. `api_behavior_report.md` — Markdown-rapport
3. `edge_cases.md` — Dokumenterade avvikelser
