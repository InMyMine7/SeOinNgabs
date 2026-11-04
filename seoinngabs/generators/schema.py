"""Schema.org JSON-LD generator."""

import json
from typing import Dict, List, Optional

from ..core.ui import ask, confirm_overwrite, fail, header, success, warn


def build_website_schema(name: str, url: str, search_url: str = "", description: str = "") -> Dict:
    """WebSite schema (+ SearchAction when search_url is given)."""
    schema: Dict = {"@context": "https://schema.org", "@type": "WebSite", "name": name, "url": url}
    if description:
        schema["description"] = description
    if search_url:
        schema["potentialAction"] = {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": search_url},
            "query-input": "required name=search_term_string",
        }
    return schema


def build_organization_schema(name: str, url: str, logo: str = "", same_as: Optional[List[str]] = None) -> Dict:
    """Organization schema with logo and social profiles."""
    schema: Dict = {"@context": "https://schema.org", "@type": "Organization", "name": name, "url": url}
    if logo:
        schema["logo"] = logo
    if same_as:
        schema["sameAs"] = same_as
    return schema


def build_article_schema(
    headline: str, url: str, image: str = "", author: str = "", date_published: str = "", publisher: str = ""
) -> Dict:
    """Article/BlogPosting schema."""
    schema: Dict = {"@context": "https://schema.org", "@type": "Article", "headline": headline, "url": url}
    if image:
        schema["image"] = image
    if author:
        schema["author"] = {"@type": "Person", "name": author}
    if date_published:
        schema["datePublished"] = date_published
    if publisher:
        schema["publisher"] = {"@type": "Organization", "name": publisher}
    return schema


def build_local_business_schema(
    name: str, url: str, street: str, city: str, region: str, postal_code: str,
    telephone: str = "", image: str = ""
) -> Dict:
    """LocalBusiness schema with a PostalAddress."""
    schema: Dict = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": name,
        "url": url,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": street,
            "addressLocality": city,
            "addressRegion": region,
            "postalCode": postal_code,
        },
    }
    if telephone:
        schema["telephone"] = telephone
    if image:
        schema["image"] = image
    return schema


def build_breadcrumb_schema(crumbs: List[Dict]) -> Dict:
    """BreadcrumbList schema from {name, url} entries (root first)."""
    items = []
    for i, crumb in enumerate(crumbs, 1):
        if not crumb.get("name") or not crumb.get("url"):
            raise ValueError(f"Breadcrumb #{i} requires both 'name' and 'url'.")
        items.append({"@type": "ListItem", "position": i, "name": crumb["name"], "item": crumb["url"]})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def render_json_ld(schema: Dict) -> str:
    """Render a schema dict as a JSON-LD script block."""
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + "\n</script>"
    )


def generate_schema_interactive() -> None:
    """Interactive: build JSON-LD for the chosen type."""
    print(header("Schema.org JSON-LD Generator", "Structured data for rich results"))
    print("  Types: 1=WebSite, 2=Organization, 3=Article, 4=LocalBusiness, 5=BreadcrumbList")
    choice = ask("Type (1-5)", "1")

    try:
        if choice == "1":
            schema = build_website_schema(
                name=ask("Site name"),
                url=ask("Site URL"),
                search_url=ask("Search URL, e.g. https://x.com/?s={search_term_string} (optional)"),
                description=ask("Description (optional)"),
            )
        elif choice == "2":
            socials = ask("Social profile URLs, comma separated (optional)")
            schema = build_organization_schema(
                name=ask("Organization name"),
                url=ask("Site URL"),
                logo=ask("Logo URL (optional)"),
                same_as=[s.strip() for s in socials.split(",") if s.strip()] or None,
            )
        elif choice == "3":
            schema = build_article_schema(
                headline=ask("Article headline"),
                url=ask("Article URL"),
                image=ask("Main image URL (optional)"),
                author=ask("Author name (optional)"),
                date_published=ask("Publish date YYYY-MM-DD (optional)"),
                publisher=ask("Publisher name (optional)"),
            )
        elif choice == "4":
            schema = build_local_business_schema(
                name=ask("Business name"),
                url=ask("Site URL"),
                street=ask("Street address"),
                city=ask("City"),
                region=ask("Region/state"),
                postal_code=ask("Postal code"),
                telephone=ask("Telephone (optional)"),
                image=ask("Image URL (optional)"),
            )
        elif choice == "5":
            crumbs = []
            print("  Enter breadcrumbs from the root (empty name to finish):")
            while True:
                cname = ask("  Name")
                if not cname:
                    break
                curl = ask("  URL")
                crumbs.append({"name": cname, "url": curl})
            schema = build_breadcrumb_schema(crumbs)
        else:
            print(fail("Invalid choice."))
            return
    except ValueError as e:
        print(fail(f"Invalid input: {e}"))
        return

    output = render_json_ld(schema)
    print(f"\n{output}")

    from pathlib import Path

    if ask("Save to schema.html? (y/n)", "n").lower() == "y":
        path = Path.cwd() / "schema.html"
        if not confirm_overwrite(str(path)):
            return
        path.write_text(output + "\n", encoding="utf-8")
        print(success(f"Saved as {path}"))
