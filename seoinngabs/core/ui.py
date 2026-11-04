"""Terminal UI helpers: ANSI colors, boxes, prompts, input handling."""

import html
import os
import sys
from typing import Callable, List, Optional

# --- ANSI color codes -------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RED = "\033[91m"
WHITE = "\033[97m"

HEADING_COLORS = {
    1: GREEN, 2: YELLOW, 3: BLUE, 4: MAGENTA, 5: CYAN, 6: RED,
}

_COLORS_ENABLED: Optional[bool] = None


def supports_color() -> bool:
    """Detect whether stdout is an interactive TTY (colors only then)."""
    global _COLORS_ENABLED
    if _COLORS_ENABLED is None:
        try:
            _COLORS_ENABLED = sys.stdout.isatty()
        except (AttributeError, ValueError):
            _COLORS_ENABLED = False
    return _COLORS_ENABLED


def paint(text: str, *codes: str) -> str:
    """Wrap text with ANSI codes when the terminal supports color."""
    if not codes or not supports_color():
        return text
    return "".join(codes) + text + RESET


# --- Boxes and separators ---------------------------------------------------

def line(char: str = "-", width: int = 62) -> str:
    """Horizontal separator line."""
    return char * width


def box(title: str, body: str = "", width: int = 62, color: str = CYAN) -> str:
    """Render a title bar box: ══ TITLE ══ plus optional body below."""
    bar = f"{color}{BOLD}{title}{RESET}"
    wrapped = f" {line('═', max(width - len(title) - 2, 3))} "
    head = f"{bar}{wrapped[:width]}"
    out = [head]
    if body:
        out.append(body)
        out.append(line("─", width))
    return "\n".join(out)


def _terminal_supports_unicode() -> bool:
    """Detect whether stdout can encode box-drawing characters."""
    try:
        "═║╔╗╚╝─✔✘ℹ".encode(sys.stdout.encoding or "ascii")
        return True
    except (LookupError, UnicodeEncodeError):
        return False


_UNICODE_OK: Optional[bool] = None


def header(title: str, subtitle: str = "") -> str:
    """Application header used by every feature screen."""
    global _UNICODE_OK
    if _UNICODE_OK is None:
        _UNICODE_OK = _terminal_supports_unicode()
    if _UNICODE_OK:
        top, bot, fill = "╔═╗", "╚═╝", "═"
    else:
        top, bot, fill = "+-+", "+-+", "-"
    parts = [""]
    width = 60
    title_line = f"{top[0]}{fill}{' SeOinNgabs '.center(width - 2, fill[0])}{top[2]}"
    parts.append(paint(title_line, CYAN))
    parts.append(paint(f"  {title}", BOLD, WHITE))
    if subtitle:
        parts.append(paint(f"  {subtitle}", DIM))
    parts.append(line(fill[0] if not _UNICODE_OK else "─"))
    return "\n".join(parts)


def success(text: str) -> str:
    mark = "✔" if _terminal_supports_unicode() else "+"
    return paint(f"  {mark} {text}", GREEN)


def warn(text: str) -> str:
    mark = "!" if not _terminal_supports_unicode() else "!"
    return paint(f"  {mark} {text}", YELLOW)


def fail(text: str) -> str:
    mark = "✘" if _terminal_supports_unicode() else "x"
    return paint(f"  {mark} {text}", RED)


def info(text: str) -> str:
    mark = "ℹ" if _terminal_supports_unicode() else "i"
    return paint(f"  {mark} {text}", CYAN)


def label_value(label: str, value, missing: str = "N/A") -> str:
    """Render '  Label . . . value' with dim label."""
    text = value if value not in (None, "", []) else missing
    return f"  {paint(label.ljust(18), DIM)} {text}"


# --- Prompts ----------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    """Input with optional default, stripped."""
    suffix = f" {paint(f'[{default}]', DIM)}" if default else ""
    try:
        return input(f"  {prompt}{suffix}: ").strip() or default
    except EOFError:
        return default


def ask_int(prompt: str, default: int = 0, minimum: Optional[int] = None,
            maximum: Optional[int] = None) -> int:
    """Input an integer with validation and default."""
    while True:
        raw = ask(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print(fail("Please enter a whole number."))
            continue
        if minimum is not None and value < minimum:
            print(fail(f"Minimum value is {minimum}."))
            continue
        if maximum is not None and value > maximum:
            print(fail(f"Maximum value is {maximum}."))
            continue
        return value


def ask_choice(prompt: str, choices: List[str], default: str = "") -> str:
    """Input restricted to a list of choices (case-insensitive)."""
    lowered = {c.lower(): c for c in choices}
    while True:
        raw = ask(prompt, default).lower()
        if raw in lowered:
            return lowered[raw]
        print(fail(f"Please choose one of: {', '.join(choices)}"))


def ask_url(prompt: str = "Page URL") -> str:
    """Input a URL (scheme optional — http:// added when missing)."""
    while True:
        url = ask(prompt)
        if url:
            return url
        print(fail("URL cannot be empty."))


def pause() -> None:
    """Wait for Enter before returning to the menu."""
    try:
        input(paint("\n  Press Enter to return to the menu...", DIM))
    except (EOFError, KeyboardInterrupt):
        pass


def confirm_overwrite(filename: str) -> bool:
    """Ask whether an existing file may be overwritten (backup offered)."""
    print(warn(f"{filename} already exists."))
    answer = ask("Overwrite it? (y = overwrite, n = cancel)", "n").lower()
    return answer.startswith("y")


# --- Misc -------------------------------------------------------------------

def clear_screen() -> None:
    """Clear the terminal (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def escape_html(value: str) -> str:
    """Escape user input for safe inclusion in generated HTML."""
    return html.escape(value, quote=True)


def progress_inline(current: int, total: int, every: int = 10, label: str = "checked") -> None:
    """Single-line progress note (no newline)."""
    if total and (current % every == 0 or current == total):
        print(f"\r  {current}/{total} {label}...{' ' * 12}", end="", flush=True)


def progress_done() -> None:
    """Finish an inline progress line."""
    print("\r" + " " * 40 + "\r", end="", flush=True)


def summarize(pairs: List[tuple]) -> None:
    """Print 'Label: value' summary rows with counts."""
    for label, value in pairs:
        print(label_value(label, value))


def heading_colored(level: int, text: str) -> str:
    """Color a heading line according to its level."""
    color = HEADING_COLORS.get(level, RESET)
    return paint(f"h{level}: {text}", color)
