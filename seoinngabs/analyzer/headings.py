"""Pemeriksa heading h1-h6 with structure validation."""

from typing import List, Tuple

from bs4 import BeautifulSoup

from .fetch import fetch_page, parse_soup


def analyze_headings(soup: BeautifulSoup) -> dict:
    """Analyze heading structure.

    Returns:
        dict: headings (list (tag, text)), h1_count, empty_headings,
        skipped_levels (list of jump messages).
    """
    headings: List[Tuple[str, str]] = []
    empty: List[str] = []
    skipped: List[str] = []
    prev_level = 0

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(tag.name[1])
        text = tag.get_text(" ", strip=True)
        headings.append((tag.name, text))
        if not text:
            empty.append(tag.name)
        if level > prev_level + 1 and prev_level != 0:
            skipped.append(f"h{prev_level} -> h{level} ({text or '(empty)'})")
        prev_level = level

    h1_count = sum(1 for name, _ in headings if name == "h1")
    return {
        "headings": headings,
        "h1_count": h1_count,
        "empty_headings": empty,
        "skipped_levels": skipped,
    }


def check_headings() -> None:
    """Interactive: print all headings plus structure warnings."""
    from ..core.ui import ask_url, fail, header, heading_colored, paint, RED, warn

    print(header("Heading Structure", "h1-h6 hierarchy check"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    result = analyze_headings(soup)
    if not result["headings"]:
        print(warn("No heading tags found on this page."))
        return
    print()
    for name, text in result["headings"]:
        print("  " + heading_colored(int(name[1]), text or "(empty)"))

    print()
    if result["h1_count"] == 0:
        print(warn("No <h1> found on this page."))
    elif result["h1_count"] > 1:
        print(warn(f"{result['h1_count']} <h1> tags found — keep exactly one."))
    if result["empty_headings"]:
        print(warn(f"Empty headings: {', '.join(result['empty_headings'])}"))
    for s in result["skipped_levels"]:
        print(paint(f"  ! Level jump: {s}", RED))
    if result["h1_count"] == 1 and not result["empty_headings"] and not result["skipped_levels"]:
        from ..core.ui import success
        print(success("Heading structure looks good."))
