"""Keyword research via Google Suggest (fix B1-B4).

Endpoint: https://suggestqueries.google.com/complete/search?output=toolbar
- Keyword di-URL-encode via params (fix B1: 'a&b' tidak terpotong lagi).
- Timeout + User-Agent + retry dari session terpusat (fix B2).
- Pakai https (fix B3).
- Parse XML dengan ElementTree, decode entity otomatis (fix B4).
"""

import xml.etree.ElementTree as ET
from typing import List

from ..core.http import get_session

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


def research_keyword(keyword: str, hl: str = "id", timeout: tuple = (10, 30)) -> List[str]:
    """Ambil saran keyword dari Google Suggest.

    Args:
        keyword: kata kunci dasar.
        hl: bahasa hasil (default 'id').
        timeout: tuple (connect, read).

    Returns:
        Daftar saran keyword; kosong bila tidak ada.
    """
    session = get_session()
    response = session.get(
        SUGGEST_URL,
        params={"output": "toolbar", "hl": hl, "q": keyword},
        timeout=timeout,
    )
    response.raise_for_status()
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        return []
    return [
        s.get("data", "").strip()
        for s in root.findall(".//suggestion")
        if s.get("data", "").strip()
    ]
