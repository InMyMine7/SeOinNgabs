"""Meta tag generator with HTML escaping."""

from pathlib import Path

from ..core.ui import GREEN, ask, confirm_overwrite, fail, header, paint, success, warn
from ..core.ui import escape_html

TWITTER_CARD_TYPES = {"summary", "summary_large_image", "player", "app"}


def validate_twitter_card(value: str) -> bool:
    return value.lower() in TWITTER_CARD_TYPES


def build_meta_tags(**fields) -> list:
    """Build the list of HTML meta tags from non-empty fields."""
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
    """Interactive: build and save meta tags to meta_tags.html."""
    print(header("Meta Tag Generator", "Title, description, OG and Twitter tags"))

    fields = {
        "title": ask("Page title (e.g. My Website)"),
        "description": ask("Page description"),
        "keywords": ask("Keywords (comma separated)"),
        "author": ask("Author name (e.g. John Doe)"),
        "canonical_url": ask("Canonical URL (optional)"),
        "og_title": ask("Open Graph title (optional)"),
        "og_description": ask("Open Graph description (optional)"),
        "og_image": ask("Open Graph image URL (optional)"),
        "twitter_card": ask("Twitter card type (summary/summary_large_image/player/app)"),
        "twitter_title": ask("Twitter title (optional)"),
        "twitter_description": ask("Twitter description (optional)"),
        "twitter_image": ask("Twitter image URL (optional)"),
    }
    if fields["twitter_card"] and not validate_twitter_card(fields["twitter_card"]):
        print(warn("Unknown twitter:card type — the tag will be skipped."))
        fields["twitter_card"] = ""

    tags = build_meta_tags(**fields)
    if not tags:
        print(fail("All fields were empty — nothing to generate."))
        return
    print(paint("  Generated meta tags:", GREEN))
    for tag in tags:
        print(f"    {tag}")

    output_path = Path.cwd() / "meta_tags.html"
    if not confirm_overwrite(str(output_path)):
        return
    output_path.write_text("\n".join(tags) + "\n", encoding="utf-8")
    print(success(f"Meta tags saved to {output_path}"))
