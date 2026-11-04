"""Banner ASCII dan daftar menu (dipindah dari main.py lama)."""

from ..core.output import colorize

BANNER = """ _____     _____ _     _____         _
|   __|___|     |_|___|   | |___ ___| |_ ___
|__   | -_|  |  | |   | | | | . | .'| . |_ -|
|_____|___|_____|_|_|_|_|___|_  |__,|___|___|
                            |___|        
[Coded By '/Mine7 || github.com/InMyMine7 || t.me/InMyMineee]
"""

MENU_ITEMS = [
    ("1", "Google Trends Scrapper"),
    ("2", "Keyword Research"),
    ("3", "Backlink Generator"),
    ("4", "Check Status Url"),
    ("5", "Check Title, Meta, URL Canonical"),
    ("6", "h1, h2, h3, h4, h5, h6 checker"),
    ("7", "Check backlink internal dan external beserta anchor text"),
    ("8", "Check Broken Links"),
    ("9", "Analisa link 403 dan 301"),
    ("10", "Analisis Kecepatan Muat Gambar di Halaman"),
    ("11", "Keyword Density Checker Tool"),
    ("12", ".htaccess File Generator Tool"),
    ("13", "Robots.txt Generator Tool"),
    ("14", "Meta Tag Generator"),
    ("15", "Terms Of Services Generator Tool"),
    ("16", "Privacy Policy Generator Tool"),
    ("17", "Disclaimer Generator Tool"),
    ("18", "Open Graph / Twitter Card Checker"),
    ("19", "Image Alt Checker"),
    ("20", "Title & Meta Length Checker + SERP Preview"),
    ("21", "Redirect Chain Tracer"),
]


def render_menu() -> str:
    """Render banner + daftar menu."""
    lines = [BANNER]
    lines.extend(f"{num}. {label}" for num, label in MENU_ITEMS)
    return "\n".join(lines)
