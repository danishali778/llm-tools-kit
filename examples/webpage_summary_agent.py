from agent_tools import ToolExecutionError
from agent_tools.tools import extract_links, fetch_url_text


URL = "https://example.com"


def main() -> None:
    try:
        text = fetch_url_text(URL)
        links = extract_links(URL)
    except ToolExecutionError as exc:
        print(f"Unable to fetch example URL: {exc}")
        return

    preview = " ".join(text.split()[:40])

    print(f"URL: {URL}")
    print(f"Text preview: {preview}")
    print(f"Link count: {len(links)}")
    if links:
        print(f"First link: {links[0]}")


if __name__ == "__main__":
    main()
