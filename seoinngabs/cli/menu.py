"""Menu interaktif SeOinNgabs (fix P5: loop, bukan sekali jalan)."""

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
from ..analyzer.redirects import analyze_404_301_links
from ..analyzer.redirect_tracer import trace_redirects_interactive
from ..analyzer.serp import check_title_meta_lengths
from ..core.output import clear_screen, colorize
from ..generators.htaccess import generate_htaccess
from ..generators.legal import generate_disclaimer, generate_privacy_policy, generate_terms
from ..generators.metatags import generate_meta_tags
from ..generators.robots import generate_robots_txt
from ..generators.schema import generate_schema_interactive
from ..generators.sitemap import generate_sitemap_interactive, validate_sitemap_interactive
from ..research.keywords import research_keyword
from ..research.trends import format_trends, get_trending_searches
from .banner import render_menu

EXIT_CHOICES = {"0", "q", "quit", "exit"}


def _trends_action() -> None:
    """Menu 1: tampilkan trending searches; error ditangkap agar menu tetap hidup."""
    try:
        trends = get_trending_searches()
        print(format_trends(trends))
    except Exception as e:
        print(colorize(f"Gagal mengambil Google Trends: {e}", "red"))


def _keyword_action() -> None:
    """Menu 2: riset keyword."""
    print("=====Keyword Research=====")
    keyword = input("Keyword Research Tool: ").strip()
    if not keyword:
        print(colorize("Keyword tidak dimasukkan.", "red"))
        return
    try:
        for suggestion in research_keyword(keyword):
            print(suggestion)
    except Exception as e:
        print(colorize(f"Gagal mengambil saran keyword: {e}", "red"))


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
}


def run_menu(once: bool = False) -> None:
    """Jalankan menu interaktif.

    Args:
        once: bila True, hanya satu kali lalu keluar (untuk kompatibilitas
            script lama / testing).
    """
    while True:
        clear_screen()
        print(render_menu())
        try:
            choice = input("Choose an option (1-25, 0/q untuk keluar): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice in EXIT_CHOICES:
            return
        action = ACTIONS.get(choice)
        if action is None:
            print(colorize("Pilihan tidak valid.", "red"))
        else:
            try:
                action()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            except Exception as e:
                print(colorize(f"Terjadi kesalahan: {e}", "red"))
        if once:
            return
        input("\nTekan Enter untuk kembali ke menu...")
