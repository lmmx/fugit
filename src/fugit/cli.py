from sys import stderr
from textwrap import indent

import defopt
from pydantic import ValidationError

from .core import diff
from .interfaces import DiffConfig

__all__ = ["run_cli"]


def configure(**defopt_kwargs) -> DiffConfig:
    defopt_kwargs.update(no_negated_flags=True)
    return defopt.run(DiffConfig, **defopt_kwargs)


def handle_validation_error(ve: ValidationError) -> None:
    error_msgs = "\n".join(str(e["ctx"]["error"]) for e in ve.errors())
    msg = "Invalid command:\n" + indent(error_msgs, prefix="- ")
    print(msg, end="\n\n", file=stderr)
    return


def run_cli():
    try:
        config = configure()
    except ValidationError as ve:
        handle_validation_error(ve)
        try:
            configure(argv=["-h"])
        except SystemExit as exc:
            exc.code = 1
            raise
    else:
        result = diff(config)
        print("\n".join(result))
