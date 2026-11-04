"""Fetch halaman + parse BeautifulSoup — fondasi semua analyzer (fix D1, D3, E5)."""

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
    """Fetch URL dengan normalisasi scheme + session terpusat.

    Bila HEAD ditolak dengan 405/501, fallback ke GET otomatis dipanggil
    caller (lihat head_or_get).
    """
    normalized = normalize_url(url)
    session = get_session()
    return session.request(
        method.upper(),
        normalized,
        allow_redirects=allow_redirects,
        timeout=timeout or (10, 30),
    )


def head_or_get(url: str, timeout: Optional[tuple] = None) -> requests.Response:
    """HEAD dulu; fallback GET bila server menolak HEAD (fix D4, H3).

    Server yang menolak HEAD biasanya membalas 405 atau 501. Untuk
    membedakan 'ditolak' dari 'rusak', fallback GET hanya dipicu oleh
    status tersebut — bukan oleh 4xx lain.
    """
    response = fetch_page(url, method="HEAD", allow_redirects=True, timeout=timeout)
    if response.status_code in (405, 501):
        response.close()
        response = fetch_page(url, method="GET", allow_redirects=True, timeout=timeout)
    return response


def parse_soup(html_content: bytes | str, parser: str = "html.parser") -> BeautifulSoup:
    """Parse HTML menjadi BeautifulSoup."""
    return BeautifulSoup(html_content, parser)


def fetch_soup(url: str) -> Tuple[requests.Response, BeautifulSoup]:
    """Fetch + parse sekaligus. Raise requests.RequestException bila gagal."""
    response = fetch_page(url)
    response.raise_for_status()
    return response, parse_soup(response.content)


def check_url_status() -> None:
    """Menu interaktif: tampilkan status code + info redirect halaman."""
    print("=====Check Url Status=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        response = fetch_page(url)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return
    print(f"\nKode respons halaman adalah: {response.status_code}")
    if response.history:
        print(f"\nURL asli (sebelum diredirect): {response.history[0].url}")
        print(f"URL redirect: {response.url}")
