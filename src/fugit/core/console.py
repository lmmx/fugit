from rich.console import Console

__all__ = ("make_console",)


def make_console(plain: bool, quiet: bool):
    color_system = None if plain else "auto"
    return Console(no_color=plain, quiet=quiet, color_system=color_system)
