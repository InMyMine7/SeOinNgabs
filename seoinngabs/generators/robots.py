"""Generator robots.txt (fix M1-M4).

Perbaikan vs main.py lama:
- Satu grup User-agent * dengan banyak Disallow (fix M1: tidak ada lagi
  grup duplikat).
- Selalu ada grup default sehingga Crawl-delay/Sitemap tidak orphan (fix M2).
- Path wajib diawali '/', trailing newline (fix M3).
- Konfirmasi sebelum menimpa (fix M4).
"""

from pathlib import Path

from ..core.output import colorize


def validate_robot_path(path: str) -> bool:
    """Path robots.txt valid: diawali '/', tanpa karakter kontrol."""
    return bool(path) and path.startswith("/") and "\n" not in path and "\r" not in path


def build_robots_txt(
    allow_all: bool = False,
    disallow_paths: list = None,
    bot_rules: list = None,
    crawl_delay: str = "",
    sitemap: str = "",
) -> str:
    """Susun konten robots.txt.

    Args:
        allow_all: izinkan semua bot (Disallow kosong).
        disallow_paths: list path untuk User-agent: *.
        bot_rules: list of (bot_name, [paths]).
        crawl_delay: nilai Crawl-delay (string, '' = tidak ada).
        sitemap: URL sitemap ('' = tidak ada).
    """
    lines = []

    if allow_all:
        lines.append("User-agent: *")
        lines.append("Disallow:")
    else:
        lines.append("User-agent: *")
        if disallow_paths:
            for p in disallow_paths:
                lines.append(f"Disallow: {p}")
        else:
            lines.append("Disallow:")

    for bot_name, paths in bot_rules or []:
        lines.append(f"User-agent: {bot_name}")
        for p in paths:
            lines.append(f"Disallow: {p}")

    if crawl_delay:
        lines.append(f"Crawl-delay: {crawl_delay}")
    if sitemap:
        lines.append(f"Sitemap: {sitemap}")

    return "\n".join(lines) + "\n"


def _confirm_overwrite(path: Path) -> bool:
    if not path.exists():
        return True
    return input(f"{path.name} sudah ada. Timpa? (y/n): ").strip().lower() == "y"


def generate_robots_txt() -> None:
    """Menu interaktif: susun dan simpan robots.txt."""
    print(colorize("===== robots.txt File Generator =====", "green"))

    print("\033[94m1. Allow or Disallow All Bots\033[0m")
    allow_all = input("Do you want to allow all bots to crawl the site? (y/n): ").strip().lower() == "y"

    disallow_paths = []
    if not allow_all:
        print("\033[94m2. Disallow Specific Paths\033[0m")
        if input("Do you want to disallow specific paths? (y/n): ").strip().lower() == "y":
            while True:
                path = input("Enter the path to disallow (e.g., /private/): ").strip()
                if validate_robot_path(path):
                    disallow_paths.append(path)
                else:
                    print(colorize("Path harus diawali '/'.", "red"))
                if input("Do you want to add another path? (y/n): ").strip().lower() != "y":
                    break

    bot_rules = []
    print("\033[94m3. Allow Specific Bots\033[0m")
    if input("Do you want to specify rules for individual bots? (y/n): ").strip().lower() == "y":
        while True:
            bot_name = input("Enter the bot name (e.g., Googlebot): ").strip()
            paths = []
            if input(f"Do you want to disallow any paths for {bot_name}? (y/n): ").strip().lower() == "y":
                while True:
                    path = input(f"Enter the path to disallow for {bot_name} (e.g., /private/): ").strip()
                    if validate_robot_path(path):
                        paths.append(path)
                    else:
                        print(colorize("Path harus diawali '/'.", "red"))
                    if input("Do you want to add another path for this bot? (y/n): ").strip().lower() != "y":
                        break
            bot_rules.append((bot_name, paths))
            if input("Do you want to add another bot? (y/n): ").strip().lower() != "y":
                break

    crawl_delay = ""
    print("\033[94m4. Set Crawl Delay\033[0m")
    if input("Do you want to set a crawl delay for all bots? (y/n): ").strip().lower() == "y":
        crawl_delay = input("Enter the delay time in seconds (e.g., 10): ").strip()

    sitemap = ""
    print("\033[94m5. Add Sitemap Location\033[0m")
    if input("Do you want to add the location of your sitemap? (y/n): ").strip().lower() == "y":
        sitemap = input("Enter the URL of your sitemap (e.g., https://example.com/sitemap.xml): ").strip()

    output_path = Path.cwd() / "robots.txt"
    if not _confirm_overwrite(output_path):
        return

    content = build_robots_txt(
        allow_all=allow_all,
        disallow_paths=disallow_paths,
        bot_rules=bot_rules,
        crawl_delay=crawl_delay,
        sitemap=sitemap,
    )
    output_path.write_text(content, encoding="utf-8")
    print(colorize("robots.txt file has been generated and saved.", "green"))
