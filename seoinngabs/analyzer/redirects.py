"""Analisis link 403/301 + redirect chain tracer."""

from ..core.ui import ask_url, fail, header, paint, GREEN, RED, warn, progress_done, progress_inline
from .fetch import fetch_page, parse_soup
from .links import check_link_status, check_urls_parallel, classify_links

REDIRECT_CODES = (301, 302, 307, 308)


def analyze_404_301_links() -> None:
    """Interactive: list 404/301/403 links found on a page."""
    print(header("403/301 Redirect Analysis", "Per-link status verification"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    result = classify_links(response.url, soup)
    links = sorted({l["href"] for l in result["internal"] + result["external"]})
    if not links:
        print(warn("No checkable links found on this page."))
        return

    print(f"\n  Checking {len(links)} links...")
    statuses = check_urls_parallel(links, progress=False)
    progress_inline(len(statuses), len(statuses), label="links")
    progress_done()

    groups = [
        ("404", [s for s in statuses if s["status_code"] == 404], "Links returning 404"),
        ("301/302", [s for s in statuses if s["status_code"] in REDIRECT_CODES], "Links redirecting (301/302/307/308)"),
        ("403", [s for s in statuses if s["status_code"] == 403], "Links returning 403 (bot-block?)"),
    ]
    print()
    for label, items, title in groups:
        if items:
            print(paint(f"  {title}:", RED))
            for r in items:
                extra = f" -> {r['final_url']}" if r.get("redirected") else ""
                print(f"    {r['url']}{extra}")
        else:
            print(paint(f"  No {label} links found.", GREEN))
