"""Broken link checker."""

from typing import List

from bs4 import BeautifulSoup

from ..core.ui import RED, YELLOW, ask_url, fail, header, paint, progress_done, progress_inline, success, warn
from .fetch import fetch_page, parse_soup
from .links import check_link_status, classify_links, check_urls_parallel

REVIEW_CODES = (403, 999)


def collect_links(url: str, soup: BeautifulSoup) -> List[str]:
    """Collect unique absolute hrefs from soup (dedup, skip non-http)."""
    result = classify_links(url, soup)
    return sorted({link["href"] for link in result["internal"] + result["external"]})


def check_broken_links() -> None:
    """Interactive: find broken links on a page."""
    print(header("Broken Links Checker", "Parallel HEAD/GET verification"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    links = collect_links(response.url, soup)
    if not links:
        print(warn("No checkable links found on this page."))
        return

    print(f"\n  Checking {len(links)} links...")
    results = check_urls_parallel(links, progress=False)
    progress_inline(len(results), len(results), label="links")
    progress_done()

    broken = [r for r in results if r["error"] is None and r["status_code"] >= 400 and r["status_code"] not in REVIEW_CODES]
    review = [r for r in results if r["error"] is None and r["status_code"] in REVIEW_CODES]
    errors = [r for r in results if r["error"] is not None]

    print()
    if broken or review or errors:
        for r in broken:
            status = r["status_code"]
            print(f"  {paint(f'[BROKEN {status}]', RED)} {r['url']}")
        for r in review:
            status = r["status_code"]
            print(f"  {paint(f'[REVIEW {status}]', YELLOW)} {r['url']} (possible bot-block — check manually)")
        for r in errors:
            print(f"  {paint('[ERROR]', RED)} {r['url']} ({r['error']})")
        print(f"\n  {len(broken)} broken, {len(review)} to review, {len(errors)} errors out of {len(results)} links.")
    else:
        print(success(f"No broken links found ({len(results)} links checked)."))
