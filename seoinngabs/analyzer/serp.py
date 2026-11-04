"""Title & meta description length checker + SERP preview (Tahap 4 fitur #3).

Batas praktik SEO (Google):
- Title: ~580 piksel ≈ 60 karakter (truncation di SERP)
- Meta description: ~920 piksel ≈ 160 karakter
SERP preview: render tampilan hasil pencarian di terminal (lebar 70 kolom).
"""

import textwrap
from typing import Dict, Optional

from ..core.output import colorize
from .fetch import fetch_page, parse_soup
from .meta import _meta_content

TITLE_LIMIT = 60
DESCRIPTION_LIMIT = 160
PREVIEW_WIDTH = 70


def analyze_title_meta_lengths(soup) -> Dict[str, Optional[dict]]:
    """Ukur panjang title & meta description.

    Returns:
        dict: title/description -> {value, length, status} (None bila tag
        tidak ada). status: 'ok' | 'too_long' | 'too_short' | 'empty'.
    """
    result: Dict[str, Optional[dict]] = {}

    title_tag = soup.title
    title = title_tag.get_text(strip=True) if title_tag else None
    if title is None:
        result["title"] = None
    else:
        length = len(title)
        if length == 0:
            status = "empty"
        elif length > TITLE_LIMIT:
            status = "too_long"
        elif length < 30:
            status = "too_short"
        else:
            status = "ok"
        result["title"] = {"value": title, "length": length, "status": status}

    description = _meta_content(soup, "name", "description")
    if description is None:
        result["description"] = None
    else:
        length = len(description)
        if length == 0:
            status = "empty"
        elif length > DESCRIPTION_LIMIT:
            status = "too_long"
        elif length < 70:
            status = "too_short"
        else:
            status = "ok"
        result["description"] = {"value": description, "length": length, "status": status}

    return result


def _truncate(text: str, limit: int) -> str:
    """Potong teks ke limit dengan elipsis di batas kata."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut + "..."


def render_serp_preview(
    title: Optional[str],
    url: str,
    description: Optional[str],
    width: int = PREVIEW_WIDTH,
) -> str:
    """Render pratinjau hasil pencarian (mirip tampilan Google SERP)."""
    t = _truncate(title or "(tanpa title)", TITLE_LIMIT)
    d = _truncate(description or "(tanpa meta description)", DESCRIPTION_LIMIT)

    lines = []
    lines.append(colorize("┌" + "─" * (width + 2) + "┐", "reset"))
    lines.append(colorize("│ Google SERP Preview" + " " * (width - 17) + "│", "reset"))
    lines.append(colorize("├" + "─" * (width + 2) + "┤", "reset"))
    for line in textwrap.wrap(t, width) or [""]:
        lines.append(colorize(f"│ {line:<{width}} │", "h3"))
    lines.append(colorize(f"│ {url:<{width}} │", "h2"))
    for line in textwrap.wrap(d, width) or [""]:
        lines.append(colorize(f"│ {line:<{width}} │", "reset"))
    lines.append(colorize("└" + "─" * (width + 2) + "┘", "reset"))
    return "\n".join(lines)


def check_title_meta_lengths() -> None:
    """Menu interaktif: panjang title/meta description + SERP preview."""
    print("=====Title & Meta Length Checker + SERP Preview=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return

    result = analyze_title_meta_lengths(soup)

    print(f"\n{colorize('Title:', 'red')} batas {TITLE_LIMIT} karakter")
    if result["title"] is None:
        print(colorize("  MISSING — tag <title> tidak ditemukan", "red"))
    else:
        t = result["title"]
        sign = {"ok": "OK", "too_long": "TERLALU PANJANG", "too_short": "TERLALU PENDEK", "empty": "KOSONG"}
        print(f"  [{colorize(sign[t['status']], 'red' if t['status'] != 'ok' else 'green')}] "
              f"{t['length']} karakter: {t['value']}")

    print(f"\n{colorize('Meta Description:', 'red')} batas {DESCRIPTION_LIMIT} karakter")
    if result["description"] is None:
        print(colorize("  MISSING — <meta name=description> tidak ditemukan", "red"))
    else:
        d = result["description"]
        sign = {"ok": "OK", "too_long": "TERLALU PANJANG", "too_short": "TERLALU PENDEK", "empty": "KOSONG"}
        print(f"  [{colorize(sign[d['status']], 'red' if d['status'] != 'ok' else 'green')}] "
              f"{d['length']} karakter: {d['value']}")

    print(f"\n{colorize('SERP Preview:', 'red')}")
    print(render_serp_preview(
        result["title"]["value"] if result["title"] else None,
        response.url,
        result["description"]["value"] if result["description"] else None,
    ))
