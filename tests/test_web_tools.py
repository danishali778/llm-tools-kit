import pytest

from agent_tools.core.errors import ToolExecutionError
from agent_tools.tools.web_tools import clean_html
from agent_tools.tools.web_tools import fetch_url_text


def test_clean_html_removes_script_and_style_content():
    html = """
    <html>
      <head><style>body { color: red; }</style></head>
      <body>
        <script>alert("x")</script>
        <h1>Hello</h1>
        <p>World</p>
      </body>
    </html>
    """

    result = clean_html(html)

    assert "alert" not in result
    assert "color: red" not in result
    assert "Hello" in result
    assert "World" in result


def test_fetch_url_text_rejects_non_http_schemes():
    with pytest.raises(ToolExecutionError):
        fetch_url_text("file:///etc/passwd")


def test_fetch_url_text_returns_cleaned_text(monkeypatch):
    class DummyResponse:
        status_code = 200
        text = "<html><body><h1>Hello</h1><p>World</p></body></html>"
        content = text.encode("utf-8")

        def raise_for_status(self):
            return None

    def fake_get(self, url):
        return DummyResponse()

    monkeypatch.setattr("httpx.Client.get", fake_get)

    result = fetch_url_text("https://example.com")

    assert "Hello" in result
    assert "World" in result


def test_fetch_url_text_rejects_oversized_response(monkeypatch):
    class DummyResponse:
        status_code = 200
        text = "x" * 20
        content = b"x" * 20

        def raise_for_status(self):
            return None

    def fake_get(self, url):
        return DummyResponse()

    monkeypatch.setattr("httpx.Client.get", fake_get)

    with pytest.raises(ToolExecutionError):
        fetch_url_text("https://example.com", max_bytes=10)
