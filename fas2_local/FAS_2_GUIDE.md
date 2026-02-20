# FAS 2 — HARVESTING & METADATA-NORMALISERING

**Status:** Ready to execute  
**Tidsuppskattning:** 1-2 timmar (varav 45 min är API-hämtning)  
**Modell:** Lokal körning med Claude-support

---

## FÖRBEREDELSER

### Kontrollera att CLI fungerar
```bash
cd /Users/davideliasson/Projects/sv-rattspraxis

# Installera paketet i dev-mode (om inte redan gjort)
pip install -e .

# Verifiera CLI
sv-rp --help
```

**Förväntat output:**
```
Usage: sv-rp [OPTIONS] COMMAND [ARGS]...

Commands:
  harvest  Harvest publications from API
  verify   Verify harvested data
  export   Export masterlist
```

---

## STEG 1: TEST-KÖRNING (liten domstol)

**Börja med RHN (12 referat) för att verifiera att allt fungerar:**
```bash
# Skapa data-mapp
mkdir -p data/raw data/processed data/logs

# Kör harvesting för RHN
sv-rp harvest --court RHN --type REFERAT

# Förväntat: 12 JSON-filer i data/raw/RHN/
ls -lh data/raw/RHN/

# Förväntat: masterlist.csv i data/processed/RHN/
cat data/processed/RHN/masterlist.csv | head -5
```

**Om detta fungerar → fortsätt till HDO**  
**Om fel → rapportera till Claude för felsökning**

---

## STEG 2: HDO HARVESTING (5,518 referat)

**Viktigt:** Detta tar 45-60 minuter. API-anrop med 1.5s delay.
```bash
# Starta HDO harvesting
sv-rp harvest --court HDO --type REFERAT --from-year 2000

# Körningen kommer visa progress:
# [INFO] harvest_start domstol=HDO from_date=2000-01-01 to_date=2026-12-31
# [INFO] harvest_initial_response total_publications=5518 total_pages=56
# [INFO] harvest_page page_index=1 total_pages=56 fetched_so_far=200
# ...
```

**Under körning:**
- Låt terminalen vara öppen
- Övervaka progress
- Om fel → Ctrl+C och rapportera till Claude

**Efter körning:**
```bash
# Kontrollera antal filer
find data/raw/HDO -name "*.json" | wc -l
# Förväntat: ~5518

# Kontrollera masterlist
wc -l data/processed/HDO/masterlist.csv
# Förväntat: ~5519 rader (header + 5518 poster)
```

---

## STEG 3: VERIFIERING

### Sekvenskontroll
```bash
# Kör verify
sv-rp verify --court HDO

# Förväntat output:
# ✓ Sekvens OK för år 2020: ref 1-45
# ✓ Sekvens OK för år 2021: ref 1-52
# ⚠ Lucka i år 2022: ref 15 saknas
# ...
```

### Manuell kontroll
```bash
# Kontrollera SHA-256 integritet
head -20 data/processed/HDO/masterlist.csv

# Kontrollera att alla målnummer parsades
grep "UNKNOWN" data/processed/HDO/masterlist.csv | wc -l
# Förväntat: 0 eller mycket få
```

---

## STEG 4: STATISTIK & DOKUMENTATION

### Samla statistik
```bash
# Totalt antal
echo "Total HDO referat: $(find data/raw/HDO -name '*.json' | wc -l)"

# Per år
for year in {2000..2026}; do
  count=$(grep "\"$year\"" data/processed/HDO/masterlist.csv | wc -l)
  echo "År $year: $count referat"
done

# Exempel på målnummerformat
head -100 data/processed/HDO/masterlist.csv | cut -d',' -f8 | sort -u
```

### Skapa rapport
```bash
cat > docs/FAS2_HDO_REPORT.md << 'REPORT'
# FAS 2 RAPPORT — HDO HARVESTING

**Datum:** $(date +%Y-%m-%d)  
**Domstol:** HDO (Högsta domstolen)  
**Typ:** REFERAT

## Resultat

- **Totalt referat:** [FYLL I]
- **Tidsperiod:** 2000-2026
- **Körning startad:** [FYLL I]
- **Körning slutförd:** [FYLL I]
- **Total tid:** [FYLL I] minuter

## Filstruktur
```
data/raw/HDO/
  ├── HDO_2020_ref-001__mal-O1234-20.json
  ├── HDO_2020_ref-002__mal-B5678-20.json
  └── ... (5,518 filer totalt)

data/processed/HDO/
  └── masterlist.csv (5,519 rader: header + 5,518 poster)
```

## Fördelning per år

[FYLL I från statistik ovan]

## Målnummerformat (exempel)

[FYLL I exempel från statistik]

## Verifiering

- ✅ Alla filer har SHA-256 hash
- ✅ Sekvenskontroll genomförd
- ⚠️ Luckor identifierade: [LISTA]
- ✅ Målnummerparsning: [X] UNKNOWN av 5,518

## Problem & lösningar

[Dokumentera eventuella problem under körning]

## Nästa steg

- Fas 1c: DOM_ELLER_BESLUT + PT (HDO har 256 + 67)
- Fas 2 (fortsättning): REGR harvesting (1,727 referat)
REPORT
```

---

## STEG 5: SAMPLE-FILER FÖR GIT

**OBS:** data/ är i .gitignore. Vi committar INTE 5,518 filer!

Istället: Spara 2-3 exempel-filer för dokumentation:
```bash
# Skapa sample-mapp
mkdir -p docs/samples/HDO

# Kopiera 3 exempel
cp data/raw/HDO/HDO_2025_ref-001__mal-*.json docs/samples/HDO/sample_001.json
cp data/raw/HDO/HDO_2025_ref-010__mal-*.json docs/samples/HDO/sample_010.json
cp data/raw/HDO/HDO_2024_ref-050__mal-*.json docs/samples/HDO/sample_050.json

# Anonymisera om nödvändigt (valfritt)
```

---

## STEG 6: COMMIT
```bash
# Lägg till dokumentation + samples
git add docs/FAS2_HDO_REPORT.md \
        docs/samples/HDO/ \
        fas2_local/

# Committa
git commit -m "feat(fas2): HDO harvesting complete - 5,518 referat

Harvested all HDO REFERAT publications from 2000-2026.

Results:
- Total: 5,518 referat
- Time period: 2000-2026
- Harvest time: ~45 minutes
- Rate limiting: 1.5s between requests
- Storage: data/raw/HDO/ (gitignored)

Verification:
- SHA-256 hashes verified
- Sequence check: [status]
- Case number parsing: [X] UNKNOWN of 5,518

Files:
- docs/FAS2_HDO_REPORT.md (detailed report)
- docs/samples/HDO/ (3 example files)

Note: Raw data (5,518 JSON files) stored locally in data/raw/HDO/
and excluded from git via .gitignore per design.

Next: Fas 1c (DOM_ELLER_BESLUT + PT) or Fas 2 cont. (REGR)"

git push origin develop
```

---

## TROUBLESHOOTING

### Problem: CLI kommando hittas inte
```bash
# Lösning: Installera i dev-mode
pip install -e .

# Verifiera
which sv-rp
sv-rp --help
```

### Problem: API timeout
```bash
# Öka timeout i api_client.py
# Eller vänta och försök igen
```

### Problem: Rate limit (429)
```bash
# Harvestern har redan backoff-logik
# Men om det händer ofta: öka delay från 1.5s till 2.0s
```

### Problem: Disk space
```bash
# Kontrollera ledigt utrymme
df -h

# 5,518 filer á ~5-50 KB = ~100-500 MB
# Behöver minst 1 GB fritt
```

### Problem: Körning avbruten
```bash
# Harvestern är INTE resumable ännu
# Om avbruten: starta om från början
# Befintliga filer skrivs över (samma filnamn)
```

---

## TIPS

1. **Kör på kvällen** — låt det jobba över natten om du vill
2. **Använd `tmux` eller `screen`** — undvik att tappa SSH-session
3. **Övervaka logs** — `tail -f data/logs/harvest_YYYYMMDD.log`
4. **Backup** — kopiera data/ till extern disk efter harvesting

---

## EFTER FAS 2

Du har nu:
- ✅ 22 domstolar konfigurerade
- ✅ Generaliserad harvester
- ✅ Robust målnummerparsning
- ✅ 5,518 HDO-referat harvested

**Nästa:**
- Fas 1c: DOM_ELLER_BESLUT + PT för HDO
- Fas 2 (fler domstolar): REGR, MIOD, etc.
- Fas 3: HTML-chunking
- Fas 4: RAG-pipeline
