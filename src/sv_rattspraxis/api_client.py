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
Asynkron REST-klient för HFD Rättspraxis API.

Hanterar:
- Rate limiting (1.5s mellan anrop)
- Retry-logik vid nätverksfel
- Typade metoder för alla endpoints
"""

import asyncio
from uuid import UUID

import httpx
import structlog

from .models import Publication, SearchRequest, SearchResponse

logger = structlog.get_logger()


class APIClient:
    """
    Asynkron klient för rattspraxis.etjanst.domstol.se/api/v1/.

    Implementerar rate limiting och retry-logik för att vara
    respektfull mot API-servern.
    """

    BASE_URL = "https://rattspraxis.etjanst.domstol.se/api/v1"
    USER_AGENT = "HFDHarvester/1.0 (Access to Justice Research)"
    RATE_LIMIT_SECONDS = 1.5
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2.0  # Exponentiell backoff-multiplikator

    def __init__(
        self,
        rate_limit: float = RATE_LIMIT_SECONDS,
        max_retries: int = MAX_RETRIES,
        timeout: float = 30.0,
    ):
        """
        Initierar API-klient.

        Args:
            rate_limit: Minsta tid mellan anrop (sekunder)
            max_retries: Max antal omförsök vid nätverksfel
            timeout: HTTP timeout (sekunder)
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"User-Agent": self.USER_AGENT},
            timeout=timeout,
        )

        logger.info(
            "api_client_initialized",
            base_url=self.BASE_URL,
            rate_limit=rate_limit,
            max_retries=max_retries,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Stänger HTTP-klienten."""
        await self.client.aclose()
        logger.info("api_client_closed")

    async def _rate_limit_wait(self):
        """
        Väntar så att rate limit respekteras.

        Använder en lock för att säkerställa att endast en request
        görs åt gången (viktigt vid parallella anrop).
        """
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_request_time

            if time_since_last < self.rate_limit:
                wait_time = self.rate_limit - time_since_last
                logger.debug("rate_limit_wait", wait_seconds=wait_time)
                await asyncio.sleep(wait_time)

            self._last_request_time = asyncio.get_event_loop().time()

    async def _request_with_retry(
        self, method: str, endpoint: str, **kwargs
    ) -> httpx.Response:
        """
        Gör HTTP-request med retry-logik.

        Args:
            method: HTTP-metod (GET, POST)
            endpoint: Endpoint-sträng (läggs till BASE_URL)
            **kwargs: Övriga argument till httpx.request()

        Returns:
            httpx.Response

        Raises:
            httpx.HTTPError: Efter max_retries misslyckade försök
        """
        await self._rate_limit_wait()

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, endpoint, **kwargs)
                response.raise_for_status()

                logger.debug(
                    "api_request_success",
                    method=method,
                    endpoint=endpoint,
                    status_code=response.status_code,
                    attempt=attempt + 1,
                )

                return response

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                is_last_attempt = attempt == self.max_retries - 1

                logger.warning(
                    "api_request_failed",
                    method=method,
                    endpoint=endpoint,
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    error=str(e),
                    will_retry=not is_last_attempt,
                )

                if is_last_attempt:
                    raise

                # Exponentiell backoff
                wait_time = self.RETRY_BACKOFF ** attempt
                await asyncio.sleep(wait_time)

        # Borde aldrig nås (raise i loopen), men för type checker
        raise RuntimeError("Unexpected code path in _request_with_retry")

    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        Söker avgöranden via POST /api/v1/sok.

        Args:
            request: SearchRequest-objekt med filter och paginering

        Returns:
            SearchResponse med lista av Publication-objekt

        Example:
            >>> client = APIClient()
            >>> request = SearchRequest(
            ...     antalPerSida=100,
            ...     sidIndex=0,
            ...     filter=SearchFilter(domstolKodLista=["HFD"])
            ... )
            >>> response = await client.search(request)
            >>> print(response.antalPubliceringar)
        """
        logger.info(
            "search_request",
            sida=request.sidIndex,
            antal_per_sida=request.antalPerSida,
            domstolar=request.filter.domstolKodLista,
            typer=request.filter.avgorandeTypLista,
        )

        response = await self._request_with_retry(
            "POST", "/sok", json=request.model_dump(exclude_none=True)
        )

        data = response.json()
        return SearchResponse(**data)

    async def get_publication(self, publication_id: UUID) -> Publication:
        """
        Hämtar enskild publikation via GET /api/v1/publiceringar/{id}.

        Args:
            publication_id: UUID från tidigare sökresultat

        Returns:
            Publication-objekt

        Example:
            >>> pub = await client.get_publication(
            ...     UUID("12345678-1234-1234-1234-123456789abc")
            ... )
        """
        logger.info("get_publication", publication_id=str(publication_id))

        response = await self._request_with_retry("GET", f"/publiceringar/{publication_id}")

        data = response.json()
        return Publication(**data)

    async def get_domstolar(self) -> list[dict[str, str]]:
        """
        Hämtar lista över alla domstolskoder via GET /api/v1/domstolar.

        Returns:
            Lista av domstolar [{domstolKod, domstolNamn}, ...]

        Example:
            >>> domstolar = await client.get_domstolar()
            >>> hfd = [d for d in domstolar if d["domstolKod"] == "HFD"][0]
            >>> print(hfd["domstolNamn"])
            Högsta förvaltningsdomstolen
        """
        logger.info("get_domstolar")

        response = await self._request_with_retry("GET", "/domstolar")
        return response.json()

    async def get_latest_publications(self, limit: int = 20) -> list[Publication]:
        """
        Hämtar senaste publikationer via GET /api/v1/publiceringar.

        Args:
            limit: Max antal att hämta

        Returns:
            Lista av Publication-objekt

        Note:
            Används främst för att verifiera API-anslutning.
            För systematisk harvesting används search().
        """
        logger.info("get_latest_publications", limit=limit)

        response = await self._request_with_retry("GET", f"/publiceringar?limit={limit}")

        data = response.json()
        return [Publication(**item) for item in data]
