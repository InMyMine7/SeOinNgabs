"""Interactive menu loop (English UI, grouped menu, numbered prompts)."""

from ..analyzer import alt
from ..analyzer.backlinks_gen import generate_backlinks
from ..analyzer.broken import check_broken_links
from ..analyzer.crawler import crawl_site_interactive
from ..analyzer.density import check_keyword_density
from ..analyzer.fetch import check_url_status
from ..analyzer.headings import check_headings
from ..analyzer.images import analyze_image_load_speed
from ..analyzer.links import analyze_backlinks
from ..analyzer.meta import check_title_meta_canonical
from ..analyzer.og import check_og_twitter
from ..analyzer.redirect_tracer import trace_redirects_interactive
from ..analyzer.redirects import analyze_404_301_links
from ..analyzer.security import check_security_interactive
from ..analyzer.serp import check_title_meta_lengths
from ..core.ui import CYAN, DIM, GREEN, ask, clear_screen, fail, header, info, paint, pause, success, warn
from ..export.exporters import export_interactive
from ..generators.htaccess import generate_htaccess
from ..generators.legal import generate_disclaimer, generate_privacy_policy, generate_terms
from ..generators.metatags import generate_meta_tags
from ..generators.robots import generate_robots_txt
from ..generators.schema import generate_schema_interactive
from ..generators.sitemap import generate_sitemap_interactive, validate_sitemap_interactive
from ..research.keywords import list_available_languages, research_keyword
from ..research.trends import format_trends, get_trending_searches, list_available_geos
from .banner import render_menu

EXIT_CHOICES = {"0", "q", "quit", "exit"}


def _trends_action() -> None:
    """Menu 1: trending searches with geo selection."""
    geos = list_available_geos()
    print(header("Google Trends Scraper", "Trending searches in your region"))
    print(paint("  Available regions:", DIM))
    codes = list(geos.keys())
    # tampilkan 16 pertama dalam 2 kolom + opsi lain
    for i in range(0, min(16, len(codes)), 2):
        left = f"{codes[i]:>2} {geos[codes[i]]:<16}"
        right = f"{codes[i+1]:>2} {geos[codes[i+1]]}" if i + 1 < len(codes) else ""
        print(f"    {left}  {right}")
    print(paint("    .. or any other Google Trends geo code", DIM))
    geo = ask("Region code", "ID").upper()
    try:
        limit = int(ask("Max results", "20"))
    except ValueError:
        limit = 20
    try:
        trends = get_trending_searches(geo=geo, limit=limit)
    except Exception as e:
        print(fail(f"Could not fetch Google Trends: {e}"))
        return
    if not trends:
        print(warn(f"No trending results for region {geo}."))
        return
    print()
    print(format_trends(trends, geo=geo))


def _keyword_action() -> None:
    """Menu 2: keyword research with language selection."""
    languages = list_available_languages()
    print(header("Keyword Research", "Google Suggest autocomplete"))
    keyword = ask("Base keyword")
    if not keyword:
        print(fail("Keyword cannot be empty."))
        return
    print(paint("  Common languages:", DIM))
    codes = list(languages.keys())
    for i in range(0, min(16, len(codes)), 4):
        row = "  ".join(f"{c}:{languages[c][:10]:<10}" for c in codes[i:i+4])
        print(f"    {row}")
    hl = ask("Language code", "id").lower()
    try:
        suggestions = research_keyword(keyword, hl=hl)
    except Exception as e:
        print(fail(f"Could not fetch suggestions: {e}"))
        return
    if not suggestions:
        print(warn("No suggestions found."))
        return
    print()
    for i, s in enumerate(suggestions, 1):
        print(f"  {paint(f'{i:>2}.', GREEN)} {s}")


ACTIONS = {
    "1": _trends_action,
    "2": _keyword_action,
    "3": generate_backlinks,
    "4": check_url_status,
    "5": check_title_meta_canonical,
    "6": check_headings,
    "7": analyze_backlinks,
    "8": check_broken_links,
    "9": analyze_404_301_links,
    "10": analyze_image_load_speed,
    "11": check_keyword_density,
    "12": generate_htaccess,
    "13": generate_robots_txt,
    "14": generate_meta_tags,
    "15": generate_terms,
    "16": generate_privacy_policy,
    "17": generate_disclaimer,
    "18": check_og_twitter,
    "19": alt.check_image_alts,
    "20": check_title_meta_lengths,
    "21": trace_redirects_interactive,
    "22": crawl_site_interactive,
    "23": generate_sitemap_interactive,
    "24": validate_sitemap_interactive,
    "25": generate_schema_interactive,
    "26": export_interactive,
    "27": check_security_interactive,
}


def run_menu(once: bool = False) -> None:
    """Run the interactive menu loop.

    Args:
        once: run a single action then return (for testing/compatibility).
    """
    while True:
        clear_screen()
        print(render_menu())
        try:
            choice = input(paint("  Choose an option (1-27, 0 = exit): ", CYAN, )).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice in EXIT_CHOICES:
            print(paint("  Goodbye!", GREEN))
            return
        action = ACTIONS.get(choice)
        if action is None:
            print(fail("Invalid choice — pick a number from the menu."))
        else:
            try:
                action()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            except Exception as e:
                print(fail(f"Something went wrong: {e}"))
        if once:
            return
        pause()
