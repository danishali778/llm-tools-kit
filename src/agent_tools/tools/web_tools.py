from __future__ import annotations

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import httpx

from agent_tools.core.errors import ToolExecutionError
from agent_tools.core.tool import tool


@tool
def clean_html(html: str) -> str:
    """Convert raw HTML into readable text."""
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in ("script", "style", "noscript"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


@tool(risk_level="medium")
def fetch_url_text(
    url: str,
    timeout_seconds: float = 10.0,
    max_bytes: int = 1_000_000,
) -> str:
    """Fetch a public webpage and return readable text."""
    html = _fetch_url_html(url, timeout_seconds=timeout_seconds, max_bytes=max_bytes)
    return clean_html(html)


def _fetch_url_html(url: str, *, timeout_seconds: float, max_bytes: int) -> str:
    _validate_url(url)
    if timeout_seconds <= 0:
        raise ToolExecutionError("timeout_seconds must be greater than 0.")
    if max_bytes < 1:
        raise ToolExecutionError("max_bytes must be greater than 0.")

    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ToolExecutionError(f"Unable to fetch URL: {url}") from exc

    if len(response.content) > max_bytes:
        raise ToolExecutionError(f"Response exceeds max_bytes limit of {max_bytes}.")

    return response.text


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ToolExecutionError("Only http and https URLs are allowed.")
    if not parsed.netloc:
        raise ToolExecutionError("URL must include a network location.")


@tool(risk_level="medium")
def extract_links(
    url: str,
    timeout_seconds: float = 10.0,
    max_bytes: int = 1_000_000,
) -> list[str]:
    """Fetch a public webpage and extract unique links."""
    html = _fetch_url_html(url, timeout_seconds=timeout_seconds, max_bytes=max_bytes)
    soup = BeautifulSoup(html, "html.parser")

    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()
        if not href or href.startswith("#"):
            continue

        absolute = urljoin(url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue

        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)

    return links
