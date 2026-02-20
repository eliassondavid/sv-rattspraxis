# FAS 2 CHECKLIST

## Pre-flight

- [ ] CLI installed (`sv-rp --help` works)
- [ ] Data directories exist (`data/raw`, `data/processed`, `data/logs`)
- [ ] Disk space: ≥1 GB free
- [ ] Network stable
- [ ] Time available: 1-2 hours

## Execution

- [ ] Test run: RHN (12 referat) ✓
- [ ] RHN verification passed
- [ ] HDO harvesting started
- [ ] HDO harvesting completed (~45 min)
- [ ] File count: ~5,518 JSON files
- [ ] Masterlist generated

## Verification

- [ ] `sv-rp verify --court HDO` passed
- [ ] Sequence check reviewed
- [ ] Målnummer parsing: <10 UNKNOWN
- [ ] SHA-256 hashes present
- [ ] Sample files look correct

## Documentation

- [ ] FAS2_HDO_REPORT.md created
- [ ] Statistics filled in
- [ ] Sample files copied to docs/samples/HDO/
- [ ] Problems documented (if any)

## Commit

- [ ] Documentation added to git
- [ ] Samples added to git
- [ ] Commit message written
- [ ] Pushed to develop

## Decision

Next step:
- [ ] Option A: Fas 1c (DOM_ELLER_BESLUT + PT for HDO)
- [ ] Option B: Fas 2 cont. (REGR, MIOD, etc.)
- [ ] Option C: Fas 3 (HTML chunking)
