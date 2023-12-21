from __future__ import annotations

from argparse import ArgumentParser
from typing import Annotated, Callable, get_args, get_origin, get_type_hints

import argh
import msgspec
from pysnooper import snoop

from ..core.diffing import load_diff
from ..core.error_handlers import CaptureInvalidConfigExit
from ..core.errors import FugitMisconfigurationExit
from ..interfaces import DiffConfig, configure_global_console

__all__ = ("run_cli",)


def stringify_hint(type_hint) -> str:
    match type_hint:
        case type():
            hint = type_hint.__name__
        case _:
            hint = str(type_hint)
    return hint


def populate_parser_descriptions(parser: ArgumentParser, struct: Callable) -> None:
    """Fill out the help attribute and instantiate any field default factories."""
    hints = get_type_hints(struct, include_extras=True)
    for action in parser._actions:
        if (flag := action.dest) in struct.__struct_fields__:
            if get_origin(hints[flag]) is Annotated:
                type_hint, meta = get_args(hints[flag])
                desc = meta.description + " "
                hint = stringify_hint(type_hint)
            else:
                # If the type is unannotated no meta so no description
                desc = ""
                hint = stringify_hint(hints[flag])
            match action.default:
                case msgspec._core.Factory() as factory_manager:
                    action.default = factory_manager.factory()
            action.help = f"{desc}(type: {hint}, default: {action.default})"


def dispatch_command(cmd: Callable, **argh_kwargs):
    """
    Replace the argh.dispatch function (str return type) specifically, by exitting early
    without calling `run_endpoint_function`, and just calling it ourselves.

    `argh_kwargs` are optional parameters for `argh.parse_and_resolve`, see its docs:

        argv: list[str] | None = None
        completion: bool = True
        namespace: argparse.Namespace | None = None
        skip_unknown_args: bool = False
    """
    parser = ArgumentParser()
    argh.set_default_command(parser, cmd)
    populate_parser_descriptions(parser, cmd)
    with CaptureInvalidConfigExit():
        _, namespace = argh.parse_and_resolve(parser=parser, **argh_kwargs)
    ns_kwargs = vars(namespace)
    ns_kwargs.pop("_functions_stack")
    result = cmd(**ns_kwargs)
    return result


def configure(**argh_kwargs) -> DiffConfig:
    """Runs argh CLI using `sys.argv`, raises `SystemExit` if the config is invalid"""
    return dispatch_command(DiffConfig, **argh_kwargs)


def run_cli() -> None:
    try:
        config = configure()
    except FugitMisconfigurationExit:
        configure(argv=["-h"])
    else:
        if config.debug:
            main = snoop(depth=1, relative_time=True)(load_diff)
        else:
            main = load_diff
        configure_global_console(config)
        _ = main(config)  # Don't return the list[str] on CLI
        return None
