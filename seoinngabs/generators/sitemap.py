"""Sitemap XML generator & validator (sitemaps.org)."""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

from ..core.ui import ask, confirm_overwrite, fail, header, success, warn

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
W3C_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?([+-]\d{2}:?\d{2}|Z)?)?$")
MAX_URLS = 50000


def build_sitemap(urls: List[Dict], pretty: bool = True) -> str:
    """Assemble a sitemap XML string from entries.

    Raises:
        ValueError: empty loc or more than MAX_URLS entries.
    """
    if len(urls) > MAX_URLS:
        raise ValueError(f"A single sitemap allows at most {MAX_URLS} URLs (got {len(urls)}).")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    indent = "    " if pretty else ""
    for entry in urls:
        loc = (entry.get("loc") or "").strip()
        if not loc:
            raise ValueError("Every sitemap entry requires 'loc'.")
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
    """Validate sitemap XML content; returns valid/errors/warnings/url_count."""
    errors: List[str] = []
    warnings: List[str] = []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {"valid": False, "errors": [f"Invalid XML: {e}"], "warnings": [], "url_count": 0}

    if root.tag != f"{{{NS}}}urlset":
        if root.tag == "urlset":
            warnings.append("Root element 'urlset' is missing the sitemaps.org namespace.")
        else:
            errors.append(f"Root element must be 'urlset' (sitemaps.org), found: {root.tag}")
            return {"valid": False, "errors": errors, "warnings": warnings, "url_count": 0}

    urls = root.findall(f"{{{NS}}}url")
    count = 0
    for i, url in enumerate(urls, 1):
        loc = url.find(f"{{{NS}}}loc")
        if loc is None or not (loc.text or "").strip():
            errors.append(f"Entry #{i}: <loc> is required and must not be empty.")
            continue
        count += 1
        text = loc.text.strip()
        parsed = urlparse(text)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append(f"Entry #{i}: <loc> must be an absolute URL, found: {text}")
        lastmod = url.find(f"{{{NS}}}lastmod")
        if lastmod is not None and lastmod.text:
            if not W3C_DATE_RE.match(lastmod.text.strip()):
                warnings.append(f"Entry #{i}: lastmod '{lastmod.text}' is not a W3C datetime (YYYY-MM-DD).")
        priority = url.find(f"{{{NS}}}priority")
        if priority is not None and priority.text:
            try:
                p = float(priority.text)
                if not (0.0 <= p <= 1.0):
                    warnings.append(f"Entry #{i}: priority {p} is outside 0.0-1.0.")
            except ValueError:
                warnings.append(f"Entry #{i}: priority '{priority.text}' is not a number.")

    if count > MAX_URLS:
        errors.append(f"A single sitemap allows at most {MAX_URLS} URLs (found {count}).")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "url_count": count}


def generate_sitemap_interactive() -> None:
    """Interactive: build sitemap.xml from user-entered URLs."""
    from pathlib import Path

    print(header("Sitemap Generator", "sitemaps.org XML from a list of URLs"))
    urls: List[Dict] = []
    print("  Enter URLs one per line (empty line to finish):")
    while True:
        try:
            loc = input("    URL: ").strip()
        except EOFError:
            break
        if not loc:
            break
        if urlparse(loc).scheme not in ("http", "https"):
            print(warn("URL must start with http:// or https:// — skipped."))
            continue
        entry: Dict = {"loc": loc}
        lastmod = ask("      lastmod YYYY-MM-DD (optional)")
        if lastmod:
            entry["lastmod"] = lastmod
        changefreq = ask("      changefreq (always/hourly/daily/weekly/monthly/yearly/never)")
        if changefreq:
            entry["changefreq"] = changefreq
        priority = ask("      priority 0.0-1.0 (optional)")
        if priority:
            try:
                entry["priority"] = float(priority)
            except ValueError:
                print(warn("Priority is not a number — ignored."))
        urls.append(entry)

    if not urls:
        print(fail("No URLs entered."))
        return

    try:
        content = build_sitemap(urls)
    except ValueError as e:
        print(fail(f"Could not build sitemap: {e}"))
        return

    report = validate_sitemap(content)
    print(success(f"Sitemap built: {len(urls)} URLs, valid={report['valid']}, warnings={len(report['warnings'])}"))
    for w in report["warnings"]:
        print(warn(w))

    output = Path.cwd() / "sitemap.xml"
    if not confirm_overwrite(str(output)):
        return
    output.write_text(content, encoding="utf-8")
    print(success(f"Saved as {output}"))


def validate_sitemap_interactive() -> None:
    """Interactive: validate a sitemap.xml file."""
    from pathlib import Path

    print(header("Sitemap Validator", "Structure and field checks"))
    path_input = ask("Sitemap file path", "sitemap.xml")
    path = Path(path_input)
    if not path.exists():
        print(fail(f"File not found: {path}"))
        return
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        print(fail(f"Could not read file: {e}"))
        return

    report = validate_sitemap(content)
    if report["valid"]:
        print(success(f"VALID — {report['url_count']} URLs found."))
    else:
        print(fail(f"NOT VALID — {len(report['errors'])} error(s):"))
        for e in report["errors"]:
            print(f"    {e}")
    for w in report["warnings"]:
        print(warn(w))
