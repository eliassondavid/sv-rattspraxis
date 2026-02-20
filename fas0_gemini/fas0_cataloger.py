import json
import time
import requests
from datetime import datetime, timezone

class SVRattspraxisCataloger:
    def __init__(self):
        self.base_url = "https://rattspraxis.etjanst.domstol.se/api/v1"
        self.headers = {
            "User-Agent": "SVRattspraxisHarvester/1.0 (Fas 0 Cataloging)",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.rate_limit = 1.5
        self.avgorande_typer = [
            "REFERAT", "NOTIS", "DOM_ELLER_BESLUT", 
            "PROVNINGSTILLSTAND", "FORHANDSAVGORANDE"
        ]
        self.test_domstolar = ["HDO", "ADO", "REGR", "HSV", "HFD"]

    def _make_request(self, method, endpoint, payload=None):
        """Centraliserad metod för att garantera rate limiting och hantera anrop."""
        time.sleep(self.rate_limit)
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=10)
            else:
                response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Nätverksfel vid {method} {endpoint}: {e}")
            return None

    def get_domstolar(self):
        """1. Hämtar alla domstolar."""
        print("Hämtar domstolslista...")
        data = self._make_request("GET", "/domstolar")
        if data and isinstance(data, list):
            return data
        return []

    def get_volumes(self, domstol_kod):
        """2. Hämtar volymer via /sok per avgörandetyp (sokforfiningar)."""
        volymer = {}
        for typ in self.avgorande_typer:
            payload = {
                "antalPerSida": 1,
                "sidIndex": 0,
                "filter": {
                    "avgorandeTypLista": [typ],
                    "domstolKodLista": [domstol_kod]
                }
            }
            data = self._make_request("POST", "/sok", payload)
            volymer[typ] = data.get("total", 0) if data else 0
        return volymer

    def get_examples_and_structure(self, domstol_kod):
        """3. Hämtar exempelposter och analyserar fältstruktur."""
        payload = {
            "antalPerSida": 5,
            "sidIndex": 0,
            "filter": {
                "domstolKodLista": [domstol_kod]
            },
            "sortorder": "avgorandedatum"
        }
        
        data = self._make_request("POST", "/sok", payload)
        poster = data.get("publiceringLista", []) if data else []
        
        struktur = {
            "innehall_tackning_procent": 0,
            "referat_nummer_format": "Saknas",
            "malnummer_format": "Saknas",
            "har_litteratur": False,
            "har_bilagor": False,
            "har_eu_echr": False
        }
        
        exempel = {"referat_nummer": [], "malnummer": []}
        innehall_count = 0

        for post in poster:
            if post.get("innehall"):
                innehall_count += 1
            
            if post.get("referatNummerLista"):
                exempel["referat_nummer"].extend(post["referatNummerLista"])
                struktur["referat_nummer_format"] = "Existerar"
                
            if post.get("malNummerLista"):
                exempel["malnummer"].extend(post["malNummerLista"])
                struktur["malnummer_format"] = "Existerar"
                
            if post.get("litteraturLista"):
                struktur["har_litteratur"] = True
            if post.get("bilagaLista"):
                struktur["har_bilagor"] = True
            if post.get("europarattsligaAvgorandenLista"):
                struktur["har_eu_echr"] = True

        if poster:
            struktur["innehall_tackning_procent"] = int((innehall_count / len(poster)) * 100)
            
        # Rensa dubbletter i exempel
        exempel["referat_nummer"] = list(set(exempel["referat_nummer"]))[:2]
        exempel["malnummer"] = list(set(exempel["malnummer"]))[:2]

        return struktur, exempel

    def test_pagination(self, domstol_kod):
        """4. Testar paginering för att identifiera överlappningar."""
        print(f"Testar paginering för {domstol_kod}...")
        
        def get_page(sid_index):
            payload = {
                "antalPerSida": 100,
                "sidIndex": sid_index,
                "filter": {"domstolKodLista": [domstol_kod]},
                "sortorder": "avgorandedatum"
            }
            data = self._make_request("POST", "/sok", payload)
            return {p.get("id") for p in data.get("publiceringLista", [])} if data else set()

        page_0 = get_page(0)
        page_1 = get_page(1)
        
        overlap = page_0.intersection(page_1)
        return list(overlap)

    def run(self):
        """Huvudfunktion för att orkestrera kartläggningen."""
        print("Startar Fas 0: API-Katalogisering...")
        domstolar = self.get_domstolar()
        
        catalog = {
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "api_base_url": self.base_url,
                "total_domstolar": len(domstolar),
                "fas": 0
            },
            "domstolar": [],
            "edge_cases": []
        }

        for domstol in domstolar:
            kod = domstol.get("domstolKod")
            namn = domstol.get("domstolNamn")
            print(f"Bearbetar: {kod} - {namn}")
            
            volymer = self.get_volumes(kod)
            struktur, exempel = self.get_examples_and_structure(kod)
            
            domstol_data = {
                "domstol_kod": kod,
                "domstol_benamning": namn,
                "volymer": volymer,
                "faltstruktur": struktur,
                "exempel": exempel,
                "avvikelser": []
            }
            catalog["domstolar"].append(domstol_data)

        # Testa paginering för utvalda instanser
        for kod in self.test_domstolar:
            if any(d["domstol_kod"] == kod for d in catalog["domstolar"]):
                over_lap = self.test_pagination(kod)
                if over_lap:
                    catalog["edge_cases"].append(
                        f"Paginering överlapp identifierad i {kod}: {len(over_lap)} ID(n) delade mellan sida 0 och 1."
                    )

        # Spara till fil
        with open("api_catalog.json", "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
            
        print("\nKartläggning slutförd. Resultat sparat i 'api_catalog.json'.")

if __name__ == "__main__":
    cataloger = SVRattspraxisCataloger()
    cataloger.run()