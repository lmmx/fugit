from .error_handlers import SuppressBrokenPipeError

__all__ = ("report",)


def report(output: str) -> None:
    with SuppressBrokenPipeError():
        print(output, end="")
