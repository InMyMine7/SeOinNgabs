"""Exception kustom SeOinNgabs."""


class SeOinNgabsError(Exception):
    """Base exception."""


class InvalidURLError(SeOinNgabsError):
    """Input URL tidak valid."""
