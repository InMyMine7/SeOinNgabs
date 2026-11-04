"""Sitemap XML generator & validator (Tahap 4 fitur #6).

Generator: susun sitemap.xml standar (sitemaps.org) dari daftar URL.
Validator: cek struktur XML, wajib <loc>, format lastmod (W3C), dan
URL absolut; laporkan masalah per entri.
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

from ..core.output import colorize

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
W3C_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?([+-]\d{2}:?\d{2}|Z)?)?$")
MAX_URLS = 50000  # batas standar sitemap tunggal


def build_sitemap(urls: List[Dict], pretty: bool = True) -> str:
    """Susun XML sitemap dari list entri.

    Args:
        urls: list of dict {loc (wajib), lastmod?, changefreq?, priority?}.
        pretty: tambah indentasi.

    Returns:
        String XML sitemap.

    Raises:
        ValueError: bila ada loc kosong atau jumlah URL melebihi batas.
    """
    if len(urls) > MAX_URLS:
        raise ValueError(f"Sitemap tunggal maksimum {MAX_URLS} URL (diberikan {len(urls)}).")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    indent = "    " if pretty else ""
    for entry in urls:
        loc = (entry.get("loc") or "").strip()
        if not loc:
            raise ValueError("Setiap entri sitemap wajib memiliki 'loc'.")
        lines.append(f"{indent}<url>")
        lines.append(f"{indent}    <loc>{xml_escape(loc)}</loc>")
        if entry.get("lastmod"):
            lines.append(f"{indent}    <lastmod>{xml_escape(str(entry['lastmod']))}</lastmod>")
        if entry.get("changefreq"):
            lines.append(f"{indent}    <changefreq>{xml_escape(str(entry['changefreq']))}</changefreq>")
        if entry.get("priority") is not None:
            lines.append(f"{indent}    <priority>{xml_escape(str(entry['priority']))}</priority>")
        lines.append(f"{indent}</url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def validate_sitemap(content: str) -> Dict:
    """Validasi konten sitemap.xml.

    Returns:
        dict: valid (bool), errors (list), warnings (list), url_count.
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {"valid": False, "errors": [f"XML tidak valid: {e}"], "warnings": [], "url_count": 0}

    if root.tag != f"{{{NS}}}urlset":
        # coba tanpa namespace (sitemap non-standar)
        if root.tag == "urlset":
            warnings.append("Elemen root 'urlset' tanpa namespace sitemaps.org.")
        else:
            errors.append(f"Elemen root harus 'urlset' (namespace sitemaps.org), ditemukan: {root.tag}")
            return {"valid": False, "errors": errors, "warnings": warnings, "url_count": 0}

    urls = root.findall(f"{{{NS}}}url")
    count = 0
    for i, url in enumerate(urls, 1):
        loc = url.find(f"{{{NS}}}loc")
        if loc is None or not (loc.text or "").strip():
            errors.append(f"Entri #{i}: elemen <loc> wajib dan tidak boleh kosong.")
            continue
        count += 1
        text = loc.text.strip()
        parsed = urlparse(text)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append(f"Entri #{i}: <loc> harus URL absolut, ditemukan: {text}")
        lastmod = url.find(f"{{{NS}}}lastmod")
        if lastmod is not None and lastmod.text:
            if not W3C_DATE_RE.match(lastmod.text.strip()):
                warnings.append(f"Entri #{i}: lastmod '{lastmod.text}' bukan format W3C datetime (YYYY-MM-DD).")
        priority = url.find(f"{{{NS}}}priority")
        if priority is not None and priority.text:
            try:
                p = float(priority.text)
                if not (0.0 <= p <= 1.0):
                    warnings.append(f"Entri #{i}: priority {p} di luar rentang 0.0-1.0.")
            except ValueError:
                warnings.append(f"Entri #{i}: priority '{priority.text}' bukan angka.")

    if count > MAX_URLS:
        errors.append(f"Sitemap tunggal maksimum {MAX_URLS} URL (ditemukan {count}).")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "url_count": count}


def generate_sitemap_interactive() -> None:
    """Menu interaktif: buat sitemap.xml dari daftar URL yang dimasukkan."""
    print(colorize("===== Sitemap Generator =====", "green"))
    urls: List[Dict] = []
    print("Masukkan URL satu per satu (kosong + Enter untuk selesai):")
    while True:
        try:
            loc = input("URL (atau kosong): ").strip()
        except EOFError:
            break
        if not loc:
            break
        if urlparse(loc).scheme not in ("http", "https"):
            print(colorize("  URL harus diawali http:// atau https:// — dilewati.", "red"))
            continue
        entry: Dict = {"loc": loc}
        lastmod = input("  lastmod YYYY-MM-DD (opsional, kosongkan): ").strip()
        if lastmod:
            entry["lastmod"] = lastmod
        changefreq = input("  changefreq always/hourly/daily/weekly/monthly/yearly/never (opsional): ").strip().lower()
        if changefreq:
            entry["changefreq"] = changefreq
        priority = input("  priority 0.0-1.0 (opsional, kosongkan): ").strip()
        if priority:
            try:
                entry["priority"] = float(priority)
            except ValueError:
                print(colorize("  priority bukan angka — diabaikan.", "red"))
        urls.append(entry)

    if not urls:
        print(colorize("Tidak ada URL yang dimasukkan.", "red"))
        return

    try:
        content = build_sitemap(urls)
    except ValueError as e:
        print(colorize(f"Gagal membuat sitemap: {e}", "red"))
        return

    report = validate_sitemap(content)
    print(f"\n{colorize('Sitemap dibuat:', 'green')} {len(urls)} URL, "
          f"valid={report['valid']}, warning={len(report['warnings'])}")
    for w in report["warnings"]:
        print(colorize(f"  [!] {w}", "red"))

    from pathlib import Path

    output = Path.cwd() / "sitemap.xml"
    if output.exists() and input("sitemap.xml sudah ada. Timpa? (y/n): ").strip().lower() != "y":
        return
    output.write_text(content, encoding="utf-8")
    print(colorize("Tersimpan sebagai sitemap.xml", "green"))


def validate_sitemap_interactive() -> None:
    """Menu interaktif: validasi file sitemap.xml."""
    print(colorize("===== Sitemap Validator =====", "green"))
    from pathlib import Path

    path_input = input("Path file sitemap (default: sitemap.xml): ").strip() or "sitemap.xml"
    path = Path(path_input)
    if not path.exists():
        print(colorize(f"File tidak ditemukan: {path}", "red"))
        return
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        print(colorize(f"Gagal membaca file: {e}", "red"))
        return

    report = validate_sitemap(content)
    if report["valid"]:
        print(colorize(f"\nVALID — {report['url_count']} URL ditemukan.", "green"))
    else:
        print(colorize(f"\nTIDAK VALID — {len(report['errors'])} error:", "red"))
        for e in report["errors"]:
            print(f"  [X] {e}")
    for w in report["warnings"]:
        print(colorize(f"  [!] {w}", "red"))
