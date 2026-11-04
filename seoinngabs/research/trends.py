"""Google Trends trending searches (fix A1-A4).

Menggunakan endpoint RSS resmi yang masih aktif:
    https://trends.google.com/trending/rss?geo=ID
Endpoint lama pytrends (trends/api/dailytrends, trendingsearches/daily/rss)
sudah 404 — pytrends tidak lagi dipakai modul ini.
"""

import xml.etree.ElementTree as ET
from datetime import date
from typing import List, Optional

import requests

from ..core.http import get_session

TRENDING_RSS_URL = "https://trends.google.com/trending/rss"

# geo code -> display name; users may pass any valid Google Trends geo code
GEO_LABELS = {
    "ID": "Indonesia", "US": "United States", "GB": "United Kingdom", "JP": "Japan",
    "IN": "India", "DE": "Germany", "FR": "France", "BR": "Brazil", "KR": "South Korea",
    "AU": "Australia", "CA": "Canada", "SG": "Singapore", "MY": "Malaysia", "TH": "Thailand",
    "PH": "Philippines", "VN": "Vietnam", "SA": "Saudi Arabia", "AE": "United Arab Emirates",
    "NL": "Netherlands", "ES": "Spain", "IT": "Italy", "RU": "Russia", "CN": "China",
    "TW": "Taiwan", "HK": "Hong Kong", "NZ": "New Zealand", "TR": "Turkey", "EG": "Egypt",
    "ZA": "South Africa", "NG": "Nigeria", "PK": "Pakistan", "BD": "Bangladesh",
}


def list_available_geos() -> dict:
    """Return the mapping of supported geo codes to display names."""
    return dict(GEO_LABELS)


def get_trending_searches(geo: str = "ID", limit: Optional[int] = 20) -> List[str]:
    """Ambil daftar trending searches dari Google Trends RSS.

    Args:
        geo: kode negara, mis. 'ID', 'US'.
        limit: jumlah maksimum hasil (default 20).

    Returns:
        Daftar kata kunci trending.

    Raises:
        requests.RequestException: bila request gagal setelah retry.
        ValueError: bila respons bukan XML RSS yang valid.
    """
    session = get_session()
    response = session.get(TRENDING_RSS_URL, params={"geo": geo.upper()}, timeout=(10, 30))
    response.raise_for_status()

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise ValueError(f"Respons Google Trends bukan XML valid: {exc}") from exc

    items = root.findall(".//item")
    trends: List[str] = []
    for item in items:
        title = item.findtext("title")
        if title and title.strip():
            trends.append(title.strip())
    if limit:
        trends = trends[:limit]
    return trends


def format_trends(trends: List[str], geo: str = "ID") -> str:
    """Format daftar tren menjadi string laporan (kompatibel output lama)."""
    label = GEO_LABELS.get(geo.upper(), geo.upper())
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"Trending Searches in {label} ({today}):"]
    lines.extend(f"{i + 1}. {t}" for i, t in enumerate(trends))
    return "\n".join(lines)
