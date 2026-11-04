"""Generator robots.txt with correct group syntax."""

from pathlib import Path

from ..core.ui import ask, confirm_overwrite, fail, header, success


def validate_robot_path(path: str) -> bool:
    """A robots.txt path must start with '/' and contain no control chars."""
    return bool(path) and path.startswith("/") and "\n" not in path and "\r" not in path


def build_robots_txt(
    allow_all: bool = False,
    disallow_paths: list = None,
    bot_rules: list = None,
    crawl_delay: str = "",
    sitemap: str = "",
) -> str:
    """Assemble robots.txt content."""
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


def generate_robots_txt() -> None:
    """Interactive: build and save robots.txt."""
    print(header("robots.txt Generator", "Crawler rules and sitemap location"))

    allow_all = ask("Allow all bots to crawl the site? (y/n)", "y").lower() == "y"

    disallow_paths = []
    if not allow_all:
        if ask("Disallow specific paths? (y/n)", "n").lower() == "y":
            while True:
                path = ask("Path to disallow (e.g. /private/)")
                if validate_robot_path(path):
                    disallow_paths.append(path)
                else:
                    print(fail("Path must start with '/'."))
                if ask("Add another path? (y/n)", "n").lower() != "y":
                    break

    bot_rules = []
    if ask("Add rules for specific bots? (y/n)", "n").lower() == "y":
        while True:
            bot_name = ask("Bot name (e.g. Googlebot)")
            paths = []
            if ask(f"Disallow paths for {bot_name}? (y/n)", "n").lower() == "y":
                while True:
                    path = ask(f"Path to disallow for {bot_name}")
                    if validate_robot_path(path):
                        paths.append(path)
                    else:
                        print(fail("Path must start with '/'."))
                    if ask("Add another path? (y/n)", "n").lower() != "y":
                        break
            bot_rules.append((bot_name, paths))
            if ask("Add another bot? (y/n)", "n").lower() != "y":
                break

    crawl_delay = ""
    if ask("Set a crawl delay for all bots? (y/n)", "n").lower() == "y":
        crawl_delay = ask("Delay in seconds (e.g. 10)", "10")

    sitemap = ""
    if ask("Add a sitemap location? (y/n)", "n").lower() == "y":
        sitemap = ask("Sitemap URL (e.g. https://example.com/sitemap.xml)")

    output_path = Path.cwd() / "robots.txt"
    if not confirm_overwrite(str(output_path)):
        return

    content = build_robots_txt(
        allow_all=allow_all,
        disallow_paths=disallow_paths,
        bot_rules=bot_rules,
        crawl_delay=crawl_delay,
        sitemap=sitemap,
    )
    output_path.write_text(content, encoding="utf-8")
    print(success(f"robots.txt written to {output_path}"))
