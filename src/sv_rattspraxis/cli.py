"""CLI för sv-rattspraxis."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click

from .courts import COURTS
from .harvester import DomstolHarvester, SUPPORTED_HARVEST_TYPES


@click.group(help="sv-rattspraxis: harvester och bearbetning")
def main() -> None:
    """Main CLI group."""


@main.command()
def init() -> None:
    """Initialize project state."""
    click.echo("Init klar. Kör: sv-rp harvest --court HFD --type REFERAT")


@main.command()
@click.option("--court", default="HFD", show_default=True, help="Domstolskod eller ALL")
@click.option(
    "--type",
    "--typ",
    "harvest_type",
    default="REFERAT",
    show_default=True,
    type=click.Choice(SUPPORTED_HARVEST_TYPES, case_sensitive=False),
)
@click.option("--from-year", default=2011, show_default=True, type=int)
@click.option("--to-year", default=None, type=int)
@click.option("--rate-limit", default=1.5, show_default=True, type=float)
@click.option(
    "--data-root",
    default="data",
    show_default=True,
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
)
def harvest(
    court: str,
    harvest_type: str,
    from_year: int,
    to_year: int | None,
    rate_limit: float,
    data_root: Path,
) -> None:
    """Harvest publications from one court or ALL configured courts."""
    selected_court = court.upper().strip()
    selected_type = harvest_type.upper().strip()

    if selected_court != "ALL" and selected_court not in COURTS:
        supported = ", ".join(sorted(COURTS.keys()))
        raise click.ClickException(
            f"Okänd domstol: {selected_court}. Använd en av: {supported} eller ALL"
        )

    courts_to_harvest = sorted(COURTS.keys()) if selected_court == "ALL" else [selected_court]
    data_root.mkdir(parents=True, exist_ok=True)

    async def run() -> int:
        try:
            from .api_client import RattspraxisAPIClient
        except ImportError as exc:  # pragma: no cover - depends on runtime environment
            raise click.ClickException(
                "APIClient saknas i installationen. Säkerställ att api_client.py är implementerad."
            ) from exc

        total_entries = 0
        async with RattspraxisAPIClient(rate_limit=rate_limit) as client:
            for court_code in courts_to_harvest:
                click.echo(
                    f"Harvest start: court={court_code}, type={selected_type}, "
                    f"period={from_year}-{to_year or 'nu'}"
                )

                harvester = DomstolHarvester(
                    data_root=data_root,
                    api_client=client,
                    domstol_kod=court_code,
                    from_year=from_year,
                    to_year=to_year,
                    typ=selected_type,
                )
                entries = await harvester.harvest_all()
                total_entries += len(entries)
                click.echo(f"Harvest klar: {court_code} ({len(entries)} poster)")

        return total_entries

    try:
        harvested = asyncio.run(run())
    except KeyboardInterrupt as exc:
        raise click.ClickException("Avbrutet av användare") from exc

    click.echo(f"Totalt hämtade poster: {harvested}")


@main.command()
@click.option("--quick", is_flag=True, default=False)
def verify(quick: bool) -> None:
    """Verify harvested data integrity."""
    click.echo(f"not implemented: quick={quick}")


@main.command()
@click.option("--format", "output_format", default="csv", show_default=True)
@click.option("--output", default="data/masterlist/", show_default=True)
def export(output_format: str, output: str) -> None:
    """Export processed data."""
    click.echo(f"not implemented: format={output_format}, output={output}")


@main.command()
def chunk() -> None:
    """Chunk normalized text for retrieval workflows."""
    click.echo("not implemented")


@main.command()
def index() -> None:
    """Index chunked data in vector/keyword backend."""
    click.echo("not implemented")


if __name__ == "__main__":
    main()
