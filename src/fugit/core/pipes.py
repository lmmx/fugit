import os
import sys

__all__ = ("pipe_cleanup",)


def pipe_cleanup() -> None:
    """Handle BrokenPipeError: redirect output to devnull"""
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    sys.exit(1)  # Python exits with error code 1 on EPIPE
