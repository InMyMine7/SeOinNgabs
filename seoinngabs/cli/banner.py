"""Terminal banner and menu item definitions (English UI)."""

from ..core.ui import BOLD, CYAN, DIM, GREEN, WHITE, paint

BANNER = r"""
 _____     _____ _     _____         _       
|   __|___|     |_|___|   | |___ ___| |_ ___ 
|__   | -_|  |  | |   | | | | . | .'| . |_ -|
|_____|___|_____|_|_|_|_|___|_  |__,|___|___|
                            |___|                              
"""

MENU_ITEMS = [
    ("Research", [
        ("1", "Google Trends Scraper"),
        ("2", "Keyword Research"),
    ]),
    ("Backlinks & Links", [
        ("3", "Backlink Generator"),
        ("7", "Internal/External Links + Anchor Text"),
        ("8", "Broken Links Checker"),
        ("9", "403/301 Redirect Analysis"),
    ]),
    ("On-Page Analysis", [
        ("4", "URL Status Checker"),
        ("5", "Title, Meta & Canonical"),
        ("6", "Heading Structure (h1-h6)"),
        ("10", "Image Load Speed"),
        ("11", "Keyword Density Checker"),
    ]),
    ("New Checkers", [
        ("18", "Open Graph / Twitter Card Checker"),
        ("19", "Image Alt Checker"),
        ("20", "Title & Meta Length + SERP Preview"),
        ("21", "Redirect Chain Tracer"),
        ("27", "HTTPS/SSL & Security Headers"),
    ]),
    ("Crawling & Reporting", [
        ("22", "Site Crawler"),
        ("23", "Sitemap Generator"),
        ("24", "Sitemap Validator"),
        ("26", "Export CSV/JSON/HTML + Batch Mode"),
    ]),
    ("Generators", [
        ("12", ".htaccess Generator"),
        ("13", "robots.txt Generator"),
        ("14", "Meta Tag Generator"),
        ("15", "Terms of Service Generator"),
        ("16", "Privacy Policy Generator"),
        ("17", "Disclaimer Generator"),
        ("25", "Schema.org JSON-LD Generator"),
    ]),
]
 
def render_banner() -> str:
    return paint(BANNER.lstrip("\n"), GREEN) + paint("Coded By '/Mine7 | github.com/InMyMine7 | t.me/minesepen\n", WHITE)


def render_menu() -> str:
    lines = [render_banner()]
    for category, items in MENU_ITEMS:
        lines.append(paint(f"  {category}", BOLD, WHITE))
        for number, label in items:
            num = paint(f"{number:>2}", GREEN)
            lines.append(f"    {num}  {label}")
        lines.append("")
    lines.append(paint("    0   Exit", GREEN))
    return "\n".join(lines)
