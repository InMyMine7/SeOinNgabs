"""Compatibility shim: old output helpers now live in core.ui."""

from .ui import clear_screen, escape_html, paint  # noqa: F401

# Old color names kept working through colorize() calls below.
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RED = "\033[91m"
WHITE = "\033[97m"

COLORS = {
    "h1": GREEN, "h2": YELLOW, "h3": BLUE, "h4": MAGENTA,
    "h5": CYAN, "h6": RED, "green": GREEN, "red": RED, "reset": RESET,
}


def colorize(text: str, color: str) -> str:
    """Legacy helper — color a single line with a named color."""
    from .ui import paint, supports_color

    code = COLORS.get(color, RESET)
    if not supports_color():
        return text
    return f"{code}{text}{RESET}"

