#!/bin/bash
# FAS 2 QUICK START

set -e

echo "=== FAS 2: HDO HARVESTING ==="
echo ""

# Kontrollera CLI
if ! command -v sv-rp &> /dev/null; then
    echo "❌ sv-rp not found. Installing..."
    pip install -e .
fi

echo "✓ CLI installed"
echo ""

# Skapa data-mappar
mkdir -p data/raw data/processed data/logs
echo "✓ Data directories created"
echo ""

# Test: RHN (12 referat)
echo "🧪 TEST: Harvesting RHN (12 referat)..."
sv-rp harvest --court RHN --type REFERAT
echo ""

# Verifiera RHN
rhn_count=$(find data/raw/RHN -name "*.json" 2>/dev/null | wc -l)
echo "✓ RHN harvested: $rhn_count files"
echo ""

if [ "$rhn_count" -lt 5 ]; then
    echo "⚠️  WARNING: Expected ~12 files, got $rhn_count"
    echo "Check logs and fix before continuing to HDO"
    exit 1
fi

# Fråga om HDO
echo "🎯 Ready to harvest HDO (5,518 referat, ~45 min)?"
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. Run manually when ready:"
    echo "  sv-rp harvest --court HDO --type REFERAT"
    exit 0
fi

# HDO harvesting
echo "🚀 Starting HDO harvesting..."
echo "This will take 45-60 minutes. Do NOT interrupt."
echo ""

start_time=$(date +%s)
sv-rp harvest --court HDO --type REFERAT --from-year 2000
end_time=$(date +%s)

duration=$((end_time - start_time))
minutes=$((duration / 60))

echo ""
echo "✅ HDO harvesting complete!"
echo "Duration: $minutes minutes"
echo ""

# Statistik
hdo_count=$(find data/raw/HDO -name "*.json" | wc -l)
echo "📊 Statistics:"
echo "  Total files: $hdo_count"
echo "  Expected: ~5,518"
echo ""

# Verifiera
echo "🔍 Running verification..."
sv-rp verify --court HDO

echo ""
echo "✅ FAS 2 COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Review: docs/FAS2_HDO_REPORT.md"
echo "2. Commit documentation"
echo "3. Decide: Fas 1c or Fas 2 (more courts)"
