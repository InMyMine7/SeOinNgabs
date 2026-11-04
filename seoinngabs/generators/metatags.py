"""Meta Tag Generator (fix N1-N4).

Perbaikan vs main.py lama:
- Semua input di-escape (fix N1: XSS/kutip tidak lagi merusak atribut).
- Tag kosong tidak digenerate (fix N2).
- twitter:card divalidasi (fix N3).
- Konfirmasi menimpa + encoding utf-8 (fix N4).
"""

from pathlib import Path

from ..core.output import colorize, escape_html

TWITTER_CARD_TYPES = {"summary", "summary_large_image", "player", "app"}


def validate_twitter_card(value: str) -> bool:
    return value.lower() in TWITTER_CARD_TYPES


def build_meta_tags(**fields) -> list:
    """Susun daftar tag HTML dari field input (yang kosong dilewati)."""
    tags = []
    e = escape_html
    if fields.get("title"):
        tags.append(f"<title>{e(fields['title'])}</title>")
    if fields.get("description"):
        tags.append(f'<meta name="description" content="{e(fields["description"])}">')
    if fields.get("keywords"):
        tags.append(f'<meta name="keywords" content="{e(fields["keywords"])}">')
    if fields.get("author"):
        tags.append(f'<meta name="author" content="{e(fields["author"])}">')
    if fields.get("canonical_url"):
        tags.append(f'<link rel="canonical" href="{e(fields["canonical_url"])}">')
    if fields.get("og_title"):
        tags.append(f'<meta property="og:title" content="{e(fields["og_title"])}">')
    if fields.get("og_description"):
        tags.append(f'<meta property="og:description" content="{e(fields["og_description"])}">')
    if fields.get("og_image"):
        tags.append(f'<meta property="og:image" content="{e(fields["og_image"])}">')
    if fields.get("twitter_card"):
        tags.append(f'<meta name="twitter:card" content="{e(fields["twitter_card"])}">')
    if fields.get("twitter_title"):
        tags.append(f'<meta name="twitter:title" content="{e(fields["twitter_title"])}">')
    if fields.get("twitter_description"):
        tags.append(f'<meta name="twitter:description" content="{e(fields["twitter_description"])}">')
    if fields.get("twitter_image"):
        tags.append(f'<meta name="twitter:image" content="{e(fields["twitter_image"])}">')
    return tags


def generate_meta_tags() -> None:
    """Menu interaktif: susun dan simpan meta tags ke meta_tags.html."""
    print(colorize("===== Meta Tag Generator =====", "green"))

    fields = {
        "title": input("\033[94mEnter the page title (e.g., My Website): \033[0m").strip(),
        "description": input("\033[94mEnter the page description: \033[0m").strip(),
        "keywords": input("\033[94mEnter the page keywords (comma separated): \033[0m").strip(),
        "author": input("\033[94mEnter the author name (e.g., John Doe): \033[0m").strip(),
        "canonical_url": input("\033[94mEnter the canonical URL of the page (optional): \033[0m").strip(),
        "og_title": input("\033[94mEnter the Open Graph title (optional): \033[0m").strip(),
        "og_description": input("\033[94mEnter the Open Graph description (optional): \033[0m").strip(),
        "og_image": input("\033[94mEnter the Open Graph image URL (optional): \033[0m").strip(),
        "twitter_card": input("\033[94mEnter Twitter card type (summary, summary_large_image, player, or app): \033[0m").strip(),
        "twitter_title": input("\033[94mEnter Twitter title (optional): \033[0m").strip(),
        "twitter_description": input("\033[94mEnter Twitter description (optional): \033[0m").strip(),
        "twitter_image": input("\033[94mEnter Twitter image URL (optional): \033[0m").strip(),
    }
    if fields["twitter_card"] and not validate_twitter_card(fields["twitter_card"]):
        print(colorize("Tipe twitter:card tidak dikenal; tag twitter:card diabaikan.", "red"))
        fields["twitter_card"] = ""

    tags = build_meta_tags(**fields)
    print(colorize("\nGenerated Meta Tags:\n", "green"))
    for tag in tags:
        print(tag)

    output_path = Path.cwd() / "meta_tags.html"
    if output_path.exists() and input("meta_tags.html sudah ada. Timpa? (y/n): ").strip().lower() != "y":
        return
    output_path.write_text("\n".join(tags) + "\n", encoding="utf-8")
    print(colorize("Meta tags have been saved to 'meta_tags.html'.", "green"))
