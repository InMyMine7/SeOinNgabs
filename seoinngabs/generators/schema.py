"""Schema.org JSON-LD generator (Tahap 4 fitur #7).

Membuat blok <script type="application/ld+json"> untuk tipe umum:
- WebSite (dengan SearchAction opsional)
- Organization
- Article / BlogPosting
- LocalBusiness (dengan alamat)
- BreadcrumbList (dari daftar nama -> URL)

Output: JSON valid (json.dumps) dengan indentasi, siap tempel di <head>.
"""

import json
from typing import Dict, List, Optional

from ..core.output import colorize


def build_website_schema(
    name: str, url: str, search_url: str = "", description: str = ""
) -> Dict:
    """Schema WebSite (+ SearchAction bila search_url diberikan: pattern {search_term_string})."""
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


def build_organization_schema(
    name: str, url: str, logo: str = "", same_as: Optional[List[str]] = None
) -> Dict:
    """Schema Organization dengan logo dan profil sosial."""
    schema: Dict = {"@context": "https://schema.org", "@type": "Organization", "name": name, "url": url}
    if logo:
        schema["logo"] = logo
    if same_as:
        schema["sameAs"] = same_as
    return schema


def build_article_schema(
    headline: str, url: str, image: str = "", author: str = "", date_published: str = "", publisher: str = ""
) -> Dict:
    """Schema Article/BlogPosting."""
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
    """Schema LocalBusiness dengan PostalAddress."""
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
    """Schema BreadcrumbList dari list {name, url} (urut dari root)."""
    items = []
    for i, crumb in enumerate(crumbs, 1):
        if not crumb.get("name") or not crumb.get("url"):
            raise ValueError(f"Breadcrumb #{i} wajib memiliki 'name' dan 'url'.")
        items.append({"@type": "ListItem", "position": i, "name": crumb["name"], "item": crumb["url"]})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def render_json_ld(schema: Dict) -> str:
    """Render dict schema menjadi blok script JSON-LD siap tempel."""
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + "\n</script>"
    )


def generate_schema_interactive() -> None:
    """Menu interaktif: susun JSON-LD sesuai tipe pilihan user."""
    print(colorize("===== Schema.org JSON-LD Generator =====", "green"))
    print("Tipe tersedia: 1=WebSite, 2=Organization, 3=Article, 4=LocalBusiness, 5=BreadcrumbList")
    choice = input("Pilih tipe (1-5): ").strip()

    try:
        if choice == "1":
            schema = build_website_schema(
                name=input("Nama situs: ").strip(),
                url=input("URL situs: ").strip(),
                search_url=input("URL pencarian, mis. https://x.com/?s={search_term_string} (opsional): ").strip(),
                description=input("Deskripsi (opsional): ").strip(),
            )
        elif choice == "2":
            socials = input("URL profil sosial, pisahkan koma (opsional): ").strip()
            schema = build_organization_schema(
                name=input("Nama organisasi: ").strip(),
                url=input("URL situs: ").strip(),
                logo=input("URL logo (opsional): ").strip(),
                same_as=[s.strip() for s in socials.split(",") if s.strip()] or None,
            )
        elif choice == "3":
            schema = build_article_schema(
                headline=input("Judul artikel: ").strip(),
                url=input("URL artikel: ").strip(),
                image=input("URL gambar utama (opsional): ").strip(),
                author=input("Nama penulis (opsional): ").strip(),
                date_published=input("Tanggal publikasi YYYY-MM-DD (opsional): ").strip(),
                publisher=input("Nama penerbit (opsional): ").strip(),
            )
        elif choice == "4":
            schema = build_local_business_schema(
                name=input("Nama bisnis: ").strip(),
                url=input("URL situs: ").strip(),
                street=input("Alamat jalan: ").strip(),
                city=input("Kota: ").strip(),
                region=input("Provinsi/wilayah: ").strip(),
                postal_code=input("Kode pos: ").strip(),
                telephone=input("Telepon (opsional): ").strip(),
                image=input("URL gambar (opsional): ").strip(),
            )
        elif choice == "5":
            crumbs = []
            print("Masukkan breadcrumb dari root (kosongkan nama untuk selesai):")
            while True:
                cname = input("  Nama: ").strip()
                if not cname:
                    break
                curl = input("  URL: ").strip()
                crumbs.append({"name": cname, "url": curl})
            schema = build_breadcrumb_schema(crumbs)
        else:
            print(colorize("Pilihan tidak valid.", "red"))
            return
    except ValueError as e:
        print(colorize(f"Input tidak valid: {e}", "red"))
        return

    output = render_json_ld(schema)
    print(f"\n{colorize('JSON-LD:', 'green')}\n{output}")

    from pathlib import Path

    save = input("\nSimpan ke schema.html? (y/n): ").strip().lower() == "y"
    if save:
        path = Path.cwd() / "schema.html"
        if path.exists() and input("schema.html sudah ada. Timpa? (y/n): ").strip().lower() != "y":
            return
        path.write_text(output + "\n", encoding="utf-8")
        print(colorize("Tersimpan sebagai schema.html", "green"))
