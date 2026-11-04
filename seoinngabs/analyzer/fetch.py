"""Fetch halaman + parse BeautifulSoup — fondasi semua analyzer."""

from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

from ..core.http import get_session
from ..core.url import normalize_url


def fetch_page(
    url: str,
    method: str = "GET",
    allow_redirects: bool = True,
    timeout: Optional[tuple] = None,
) -> requests.Response:
    """Fetch URL with scheme normalization + shared session."""
    normalized = normalize_url(url)
    session = get_session()
    return session.request(
        method.upper(),
        normalized,
        allow_redirects=allow_redirects,
        timeout=timeout or (10, 30),
    )


def head_or_get(url: str, timeout: Optional[tuple] = None) -> requests.Response:
    """HEAD first; fall back to GET when the server rejects HEAD (405/501)."""
    response = fetch_page(url, method="HEAD", allow_redirects=True, timeout=timeout)
    if response.status_code in (405, 501):
        response.close()
        response = fetch_page(url, method="GET", allow_redirects=True, timeout=timeout)
    return response


def parse_soup(html_content, parser: str = "html.parser") -> BeautifulSoup:
    """Parse HTML into BeautifulSoup."""
    return BeautifulSoup(html_content, parser)


def fetch_soup(url: str) -> Tuple[requests.Response, BeautifulSoup]:
    """Fetch + parse; raise requests.RequestException on failure."""
    response = fetch_page(url)
    response.raise_for_status()
    return response, parse_soup(response.content)


def check_url_status() -> None:
    """Interactive: show status code and redirect info for a page."""
    from ..core.ui import ask_url, fail, header, label_value

    print(header("URL Status Checker", "Response code and redirect chain"))
    url = ask_url()
    try:
        response = fetch_page(url)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return
    print()
    print(label_value("Status code", response.status_code))
    if response.history:
        print(label_value("Original URL", response.history[0].url))
        print(label_value("Final URL", response.url))
