# Copyright 2026 David Eliasson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
CLI för HFD Rättspraxis Harvester.

Kommandon:
- hfd init --accept-terms    Godkänn upstream-villkor
- hfd harvest                 Hämta alla referat
- hfd verify                  Verifiera hämtad data
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

import structlog
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from . import __version__
from .api_client import APIClient
from .harvester import Harvester
from .verify import Verifier

# Konfigurera structlog för pretty output
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

app = typer.Typer(
    name="hfd",
    help="HFD Rättspraxis — Harvester & RAG-pipeline",
    add_completion=False,
)

console = Console()

TERMS_TEXT = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    UPSTREAM-VILLKOR & OFFENTLIGHETSPRINCIPEN              ║
╚═══════════════════════════════════════════════════════════════════════════╝

Detta verktyg hämtar data från Domstolsverkets API:
  rattspraxis.etjanst.domstol.se/api/v1/

DATAKÄLLA:
  - HFD-referat (Högsta förvaltningsdomstolen)
  - Offentliga handlingar enligt Offentlighetsprincipen (SFS 1949:105)
  - Inga personuppgifter i metadata (målnummer är anonymiserade)

ANVÄNDNING:
  - Forskning, utbildning, rättshjälp
  - INTE för kommersiell exploatering utan tillstånd
  - Respektera API:ts rate limits (1.5s mellan anrop)

ANSVAR:
  - Du ansvarar för att verifiera källors korrekthet
  - Ingen garanti för fullständighet eller aktualitet
  - Vid tvivel — kontrollera mot original på domstol.se

RATE LIMITING:
  - Harvester väntar 1.5s mellan varje API-anrop
  - Total tid: ~30 minuter för 1 117 referat
  - Var respektfull mot API-servern

Genom att acceptera dessa villkor bekräftar du att du har läst och förstått ovan.
"""


def get_data_root() -> Path:
    """Returnerar data/-katalogen (skapar om den inte finns)."""
    data_root = Path.cwd() / "data"
    data_root.mkdir(exist_ok=True)
    return data_root


def check_terms_accepted() -> bool:
    """Kontrollerar om terms har accepterats."""
    terms_file = get_data_root() / ".terms_accepted"
    return terms_file.exists()


def save_terms_accepted():
    """Sparar att terms har accepterats."""
    terms_file = get_data_root() / ".terms_accepted"
    terms_file.write_text(f"Accepted at: {datetime.now().isoformat()}\n")
    logger.info("terms_accepted", file=str(terms_file))


@app.command()
def init(
    accept_terms: bool = typer.Option(
        False,
        "--accept-terms",
        help="Godkänn upstream-villkor utan prompt",
    )
):
    """
    Initialisera harvester — godkänn upstream-villkor.

    Kräver explicit godkännande via --accept-terms.
    """
    console.print(Panel(TERMS_TEXT, title="📜 VILLKOR", border_style="blue"))

    if check_terms_accepted():
        console.print("\n✅ Villkor redan accepterade.\n", style="green")
        return

    if not accept_terms:
        accept_terms = Confirm.ask("\nAccepterar du dessa villkor?")

    if accept_terms:
        save_terms_accepted()
        console.print("\n✅ Villkor accepterade. Kör nu: hfd harvest\n", style="green")
    else:
        console.print("\n❌ Villkor EJ accepterade. Avbryter.\n", style="red")
        raise typer.Exit(code=1)


@app.command()
def harvest(
    from_year: int = typer.Option(2011, help="Starta från detta år (inkluderat)"),
    to_year: int = typer.Option(None, help="Sluta vid detta år (inkluderat), None=nuvarande"),
    typ: str = typer.Option("REFERAT", help="Typ: REFERAT eller NOTIS"),
    rate_limit: float = typer.Option(1.5, help="Minsta tid mellan API-anrop (sekunder)"),
):
    """
    Hämta alla HFD-referat via API.

    Sparar:
    - data/raw/{filnamn}.json — rå API-svar
    - data/processed/masterlist.csv — index över alla referat

    Exempel:
        hfd harvest                           # Alla referat 2011-nu
        hfd harvest --from-year 2020          # Endast 2020-nu
        hfd harvest --typ NOTIS               # Hämta notiser istället
    """
    # Kontrollera terms
    if not check_terms_accepted():
        console.print(
            "\n❌ Du måste först acceptera villkor: hfd init --accept-terms\n",
            style="red",
        )
        raise typer.Exit(code=1)

    data_root = get_data_root()

    console.print(
        Panel(
            f"🚀 Startar harvesting av {typ}\n"
            f"📅 Period: {from_year}–{to_year or 'nu'}\n"
            f"📂 Data root: {data_root}\n"
            f"⏱️  Rate limit: {rate_limit}s",
            title="HARVEST",
            border_style="green",
        )
    )

    async def run_harvest():
        async with APIClient(rate_limit=rate_limit) as client:
            harvester = Harvester(
                data_root=data_root,
                api_client=client,
                from_year=from_year,
                to_year=to_year,
                typ=typ,
            )

            entries = await harvester.harvest_all()

            console.print(
                f"\n✅ Harvesting slutförd: {len(entries)} {typ.lower()} hämtade\n",
                style="green bold",
            )

    try:
        asyncio.run(run_harvest())
    except KeyboardInterrupt:
        console.print("\n⚠️  Avbrutet av användare\n", style="yellow")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n❌ Fel vid harvesting: {e}\n", style="red")
        logger.error("harvest_failed", error=str(e), exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def verify():
    """
    Verifiera hämtad data.

    Kontrollerar:
    - Sekvenskontinuitet (ref 1→N per år)
    - SHA-256 checksums
    - Att alla filer existerar
    - Inga dubbletter

    Exempel:
        hfd verify
    """
    data_root = get_data_root()

    console.print(
        Panel(
            f"🔍 Verifierar data\n"
            f"📂 Data root: {data_root}",
            title="VERIFY",
            border_style="blue",
        )
    )

    try:
        verifier = Verifier(data_root=data_root)
        report = verifier.verify_all()

        if report.is_valid():
            console.print("\n✅ Verifiering OK — inga fel hittades\n", style="green bold")
            return  # Exit cleanly without raising exception
        else:
            console.print(
                "\n❌ Verifiering misslyckades — se logg för detaljer\n",
                style="red bold",
            )
            raise typer.Exit(code=1)

    except FileNotFoundError as e:
        console.print(f"\n❌ {e}\n", style="red")
        console.print("💡 Kör först: hfd harvest\n", style="yellow")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"\n❌ Fel vid verifiering: {e}\n", style="red")
        logger.error("verify_failed", error=str(e), exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def version():
    """Visa version."""
    console.print(f"hfd-rattspraxis v{__version__}")


if __name__ == "__main__":
    app()
