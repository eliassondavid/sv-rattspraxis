.PHONY: install test lint format clean harvest verify export help

help:
	@echo "Tillgängliga kommandon:"
	@echo "  make install       - Installera paket med dev-beroenden"
	@echo "  make test          - Kör tester med coverage"
	@echo "  make lint          - Linting med ruff och mypy"
	@echo "  make format        - Formatera kod med ruff"
	@echo "  make clean         - Rensa temporära filer och data"
	@echo "  make harvest-hfd   - Harvesta HFD referat"
	@echo "  make harvest-hdo   - Harvesta HDO referat"
	@echo "  make harvest-all   - Harvesta alla domstolar (VARNING: tar lång tid)"
	@echo "  make verify        - Verifiera integritet"
	@echo "  make export        - Exportera masterlist"

install:
	pip install -e ".[dev]"

test:
	pytest --cov=sv_rattspraxis --cov-report=term-missing --cov-report=html -v

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

harvest-hfd:
	sv-rp harvest --court HFD --type referat

harvest-hdo:
	sv-rp harvest --court HDO --type referat

harvest-regr:
	sv-rp harvest --court REGR --type referat

harvest-all:
	@echo "VARNING: Detta kommer att harvesta alla 22 domstolar och tar lång tid."
	@echo "Tryck Ctrl+C för att avbryta, Enter för att fortsätta..."
	@read
	sv-rp harvest --court ALL --type referat

verify:
	sv-rp verify

export:
	sv-rp export --format csv --output data/masterlist/

clean:
	@echo "Rensar temporära filer..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Klart!"

clean-data:
	@echo "VARNING: Detta kommer att radera ALL harvesterad data!"
	@echo "Tryck Ctrl+C för att avbryta, Enter för att fortsätta..."
	@read
	rm -rf data/raw/
	rm -rf data/processed/
	rm -rf data/html/
	rm -rf data/chunks/
	rm -rf data/masterlist/
	@echo "Data rensad!"

clean-all: clean clean-data
	@echo "Allt rensat!"
