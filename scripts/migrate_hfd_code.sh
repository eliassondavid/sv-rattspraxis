#!/bin/bash
# migrate_hfd_code.sh
# Migrera HFD-kod från gamla strukturen till sv-rattspraxis
#
# Copyright 2026 David Eliasson
# Licensed under the Apache License, Version 2.0

set -e  # Avsluta vid fel

# Färger för output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== HFD-kod migrering till sv-rattspraxis ===${NC}\n"

# Kontrollera att vi är i rätt mapp
if [ ! -f "README.md" ] || [ ! -d "src/sv_rattspraxis" ]; then
    echo -e "${RED}Fel: Detta skript måste köras från sv-rattspraxis root-mappen${NC}"
    echo "Kör: cd /path/to/sv-rattspraxis && ./migrate_hfd_code.sh"
    exit 1
fi

# Sökväg till gamla HFD-koden
OLD_HFD_PATH="/Users/davideliasson/Downloads/hfd-rattspraxis"
OLD_HFD_SRC="${OLD_HFD_PATH}/src/hfd_rattspraxis"

if [ ! -d "$OLD_HFD_PATH" ]; then
    echo -e "${RED}Fel: Hittar inte HFD-mappen på: $OLD_HFD_PATH${NC}"
    echo "Justera OLD_HFD_PATH i skriptet om mappen ligger någon annanstans."
    exit 1
fi

if [ ! -d "$OLD_HFD_SRC" ]; then
    echo -e "${RED}Fel: Hittar inte källkoden i: $OLD_HFD_SRC${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Hittar HFD-kod i: $OLD_HFD_SRC\n"

# Apache 2.0 header som ska läggas till
APACHE_HEADER="# Copyright 2026 David Eliasson
#
# Licensed under the Apache License, Version 2.0 (the \"License\");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an \"AS IS\" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"

# Funktion för att lägga till Apache-header i en Python-fil
add_apache_header() {
    local file=$1
    local temp_file="${file}.tmp"
    
    # Kolla om filen redan har Apache-header
    if grep -q "Licensed under the Apache License" "$file" 2>/dev/null; then
        echo -e "  ${YELLOW}↷${NC} Har redan Apache-header: $(basename $file)"
        return
    fi
    
    # Lägg till header
    echo "$APACHE_HEADER" > "$temp_file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"
    
    echo -e "  ${GREEN}✓${NC} Apache-header tillagd: $(basename $file)"
}

# Funktion för att kopiera och uppdatera en Python-fil
migrate_python_file() {
    local filename=$1
    local source="${OLD_HFD_SRC}/${filename}"
    local dest="src/sv_rattspraxis/${filename}"
    
    # Hoppa över backup-filer
    if [[ "$filename" == *.backup* ]] || [[ "$filename" == *.bak ]]; then
        return
    fi
    
    if [ ! -f "$source" ]; then
        echo -e "  ${YELLOW}⊘${NC} Hittar inte: $filename (hoppar över)"
        return
    fi
    
    # Kopiera fil
    cp "$source" "$dest"
    echo -e "  ${GREEN}✓${NC} Kopierad: $filename"
    
    # Lägg till Apache-header
    add_apache_header "$dest"
}

echo -e "${BLUE}Kopierar Python-filer...${NC}\n"

# Lista över förväntade HFD-filer (justera efter din faktiska struktur)
PYTHON_FILES=(
    "api_client.py"
    "models.py"
    "harvester.py"
    "naming.py"
    "verify.py"
    "cli.py"
    "html_parser.py"
    "export.py"
)

for file in "${PYTHON_FILES[@]}"; do
    migrate_python_file "$file"
done

echo ""

# Kopiera eventuella testfiler
echo -e "${BLUE}Kopierar testfiler (om de finns)...${NC}\n"

if [ -d "${OLD_HFD_PATH}/tests" ]; then
    cp -r "${OLD_HFD_PATH}/tests/"* tests/ 2>/dev/null || true
    
    # Lägg till Apache-header i alla testfiler
    for test_file in tests/test_*.py; do
        if [ -f "$test_file" ]; then
            add_apache_header "$test_file"
        fi
    done
    
    echo -e "  ${GREEN}✓${NC} Testfiler kopierade"
else
    echo -e "  ${YELLOW}⊘${NC} Ingen tests-mapp hittades"
fi

echo ""

# Kopiera eventuella fixtures
echo -e "${BLUE}Kopierar fixtures (om de finns)...${NC}\n"

if [ -d "${OLD_HFD_PATH}/fixtures" ]; then
    mkdir -p tests/fixtures
    cp -r "${OLD_HFD_PATH}/fixtures/"* tests/fixtures/ 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Fixtures kopierade"
else
    echo -e "  ${YELLOW}⊘${NC} Ingen fixtures-mapp hittades"
fi

echo ""

# Sammanfattning
echo -e "${BLUE}=== Migrering klar! ===${NC}\n"
echo -e "${GREEN}Nästa steg:${NC}"
echo "1. Kontrollera att alla filer är på plats:"
echo "   ls -la src/sv_rattspraxis/"
echo ""
echo "2. Installera och testa:"
echo "   pip install -e \".[dev]\""
echo "   make test"
echo ""
echo "3. Kör linting:"
echo "   make lint"
echo ""
echo "4. Första commit:"
echo "   git add ."
echo "   git commit -m \"feat: migrate HFD harvester code with Apache 2.0 headers\""
echo ""
echo -e "${YELLOW}OBS:${NC} Granska alla filer innan commit - kontrollera att:"
echo "  • Alla imports fortfarande fungerar"
echo "  • Apache-headers ser korrekta ut"
echo "  • Ingen känslig data (API-nycklar etc.) följde med"
echo ""
