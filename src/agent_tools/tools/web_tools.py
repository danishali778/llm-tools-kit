from __future__ import annotations

from bs4 import BeautifulSoup

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
