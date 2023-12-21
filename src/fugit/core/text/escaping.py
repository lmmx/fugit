__all__ = ("escape", "esc_pair")


def escape(desc: str, on: bool) -> tuple[str, str]:
    """Return the ANSI code to escape (on/off) the described effect."""
    return ""


def esc_pair(desc: str) -> tuple[str, str]:
    """Return the ANSI code to escape (on and off) the described effect."""
    return tuple(escape(desc, on=toggle) for toggle in (True, False))
