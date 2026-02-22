"""Utilities for PDF extraction from bilagor endpoints."""

from __future__ import annotations

import io
from typing import Any


def _resolve_bilaga_url(bilaga_id: str, base_url: str | None = None) -> str:
    if not bilaga_id or not bilaga_id.strip():
        raise ValueError("bilaga_id får inte vara tom")

    if base_url:
        return f"{base_url.rstrip('/')}/bilagor/{bilaga_id}"
    return f"/api/v1/bilagor/{bilaga_id}"


async def _fetch_pdf_bytes(api_client: Any, bilaga_id: str, base_url: str | None = None) -> bytes:
    """Fetches PDF bytes from `/api/v1/bilagor/{id}` via provided API client."""
    url = _resolve_bilaga_url(bilaga_id, base_url=base_url)

    if hasattr(api_client, "get_bilaga_bytes"):
        result = await api_client.get_bilaga_bytes(bilaga_id)
        if isinstance(result, bytes):
            return result
        raise TypeError("APIClient.get_bilaga_bytes måste returnera bytes")

    if not hasattr(api_client, "get"):
        raise TypeError("api_client måste implementera async get(url)")

    response = await api_client.get(url)
    if isinstance(response, bytes):
        return response

    if hasattr(response, "raise_for_status"):
        response.raise_for_status()

    content = getattr(response, "content", None)
    if isinstance(content, bytes):
        return content

    raise TypeError("Kunde inte tolka PDF-responsen som bytes")


def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        return ""

    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError(
            "pdfplumber saknas. Installera med: pip install pdfplumber"
        ) from exc

    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())
    return "\n\n".join(pages)


async def extract_pdf_text(api_client: Any, bilaga_id: str, base_url: str | None = None) -> str:
    """Hämtar PDF från bilaga-endpoint och extraherar textinnehåll."""
    pdf_bytes = await _fetch_pdf_bytes(api_client=api_client, bilaga_id=bilaga_id, base_url=base_url)
    return _extract_text_from_pdf_bytes(pdf_bytes)

