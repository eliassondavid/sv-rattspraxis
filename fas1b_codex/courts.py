"""Domstolskonfiguration för svensk rättspraxis-harvesting."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CourtConfig:
    """Statisk konfiguration för en domstolskod i API:t."""

    kod: str
    namn: str
    referat_format: str
    malnummer_format: str
    prioritet: int
    volymer: dict[str, int]
    har_innehall: bool
    har_bilagor: bool
    kommentar: str = ""


# 22 domstolar från api_catalog.json.
# DOV (Domstolsverket) exkluderas eftersom den inte är en publicerande domstol
# i materialet (0 volymer i alla typer).
COURTS: dict[str, CourtConfig] = {
    "ADO": CourtConfig(
        kod="ADO",
        namn="Arbetsdomstolen",
        referat_format="AD YYYY nr N",
        malnummer_format="A NNN/NN",
        prioritet=2,
        volymer={
            "REFERAT": 1979,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HDO": CourtConfig(
        kod="HDO",
        namn="Högsta domstolen",
        referat_format="NJA YYYY s. N",
        malnummer_format="X NNNN-NN",
        prioritet=1,
        volymer={
            "REFERAT": 5196,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 256,
            "PROVNINGSTILLSTAND": 67,
            "FORHANDSAVGORANDE": 2,
        },
        har_innehall=False,
        har_bilagor=True,
        kommentar="Hög volym, ofta utan referatNummer i API-sökresultat.",
    ),
    "HFD": CourtConfig(
        kod="HFD",
        namn="Högsta förvaltningsdomstolen",
        referat_format="HFD YYYY ref. N",
        malnummer_format="NNNN-NN",
        prioritet=1,
        volymer={
            "REFERAT": 1117,
            "NOTIS": 47,
            "DOM_ELLER_BESLUT": 136,
            "PROVNINGSTILLSTAND": 42,
            "FORHANDSAVGORANDE": 2,
        },
        har_innehall=True,
        har_bilagor=True,
    ),
    "HGO": CourtConfig(
        kod="HGO",
        namn="Göta hovrätt",
        referat_format="RH YYYY:N",
        malnummer_format="X NNNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 439,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HNN": CourtConfig(
        kod="HNN",
        namn="Hovrätten för Nedre Norrland",
        referat_format="RH YYYY:N",
        malnummer_format="XX NNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 200,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HON": CourtConfig(
        kod="HON",
        namn="Hovrätten för Övre Norrland",
        referat_format="RH YYYY:N",
        malnummer_format="X NNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 168,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HSB": CourtConfig(
        kod="HSB",
        namn="Hovrätten över Skåne och Blekinge",
        referat_format="RH YYYY:N",
        malnummer_format="X NNNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 508,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HSV": CourtConfig(
        kod="HSV",
        namn="Svea hovrätt",
        referat_format="RH YYYY:N",
        malnummer_format="X NNNNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 1374,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HVS": CourtConfig(
        kod="HVS",
        namn="Hovrätten för Västra Sverige",
        referat_format="RH YYYY:N",
        malnummer_format="X NNNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 630,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "HYOD": CourtConfig(
        kod="HYOD",
        namn="Svea hovrätts hyresrättsliga avgöranden",
        referat_format="RH YYYY:N",
        malnummer_format="X NNNNN-NN",
        prioritet=3,
        volymer={
            "REFERAT": 238,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 8,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=True,
    ),
    "KGG": CourtConfig(
        kod="KGG",
        namn="Kammarrätten i Göteborg",
        referat_format="Saknas",
        malnummer_format="NNN-NN",
        prioritet=4,
        volymer={
            "REFERAT": 8,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=False,
        har_bilagor=False,
        kommentar="Historisk lågvolym, ofta utan referatNummer.",
    ),
    "KJO": CourtConfig(
        kod="KJO",
        namn="Kammarrätten i Jönköping",
        referat_format="Saknas",
        malnummer_format="NNNN-NN",
        prioritet=4,
        volymer={
            "REFERAT": 23,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=False,
        har_bilagor=False,
    ),
    "KST": CourtConfig(
        kod="KST",
        namn="Kammarrätten i Stockholm",
        referat_format="RK YYYY:N",
        malnummer_format="NNNN-NN",
        prioritet=4,
        volymer={
            "REFERAT": 75,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "KSU": CourtConfig(
        kod="KSU",
        namn="Kammarrätten i Sundsvall",
        referat_format="Saknas",
        malnummer_format="NNNN-NN",
        prioritet=4,
        volymer={
            "REFERAT": 3,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=False,
        har_bilagor=False,
    ),
    "MDO": CourtConfig(
        kod="MDO",
        namn="Marknadsdomstolen",
        referat_format="MD YYYY:N",
        malnummer_format="YYYY-N",
        prioritet=2,
        volymer={
            "REFERAT": 478,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "MIOD": CourtConfig(
        kod="MIOD",
        namn="Migrationsöverdomstolen",
        referat_format="MIG YYYY:N",
        malnummer_format="XX NNNNN-NN",
        prioritet=2,
        volymer={
            "REFERAT": 526,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "MMOD": CourtConfig(
        kod="MMOD",
        namn="Mark- och miljööverdomstolen",
        referat_format="Saknas",
        malnummer_format="M NNNNN-NN",
        prioritet=2,
        volymer={
            "REFERAT": 685,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 383,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 1,
        },
        har_innehall=False,
        har_bilagor=True,
        kommentar="Både referat och domar; innehåll finns ofta i bilagor.",
    ),
    "MOD": CourtConfig(
        kod="MOD",
        namn="Miljööverdomstolen",
        referat_format="MÖD YYYY:N",
        malnummer_format="M NNNN-NN",
        prioritet=2,
        volymer={
            "REFERAT": 709,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "PBR": CourtConfig(
        kod="PBR",
        namn="Patentbesvärsrätten",
        referat_format="Saknas",
        malnummer_format="NN-NNN",
        prioritet=5,
        volymer={
            "REFERAT": 0,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 87,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=False,
        har_bilagor=False,
    ),
    "PMOD": CourtConfig(
        kod="PMOD",
        namn="Patent- och marknadsöverdomstolen",
        referat_format="Saknas",
        malnummer_format="XXX NNNNN-NN",
        prioritet=2,
        volymer={
            "REFERAT": 198,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 29,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=True,
    ),
    "REGR": CourtConfig(
        kod="REGR",
        namn="Regeringsrätten",
        referat_format="RÅ YYYY ref. N",
        malnummer_format="NNNN-NN",
        prioritet=1,
        volymer={
            "REFERAT": 1727,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 0,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=True,
        har_bilagor=False,
    ),
    "RHN": CourtConfig(
        kod="RHN",
        namn="Rättshjälpsnämnden",
        referat_format="Saknas",
        malnummer_format="NN-NN",
        prioritet=5,
        volymer={
            "REFERAT": 0,
            "NOTIS": 0,
            "DOM_ELLER_BESLUT": 12,
            "PROVNINGSTILLSTAND": 0,
            "FORHANDSAVGORANDE": 0,
        },
        har_innehall=False,
        har_bilagor=False,
    ),
}


def get_court_config(domstol_kod: str) -> CourtConfig:
    """Hämtar konfiguration för en domstolskod."""
    normalized = domstol_kod.upper()
    if normalized not in COURTS:
        raise KeyError(f"Okänd domstolskod: {domstol_kod}")
    return COURTS[normalized]
