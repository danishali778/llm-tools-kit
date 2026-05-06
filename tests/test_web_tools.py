from agent_tools.tools.web_tools import clean_html


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
