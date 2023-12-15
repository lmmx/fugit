from typing import Literal

__all__ = (
    "FugitErrorCodes",
    "FugitUserError",
    "FugitMisconfigurationExit",
)

ERROR_DOCS_URL = "https://fugit.readthedocs.io/en/latest/reference/"

FugitErrorCodes = Literal["invalid-config"]

# try:
#     configure(argv=["-h"])
# except SystemExit as exc:
#     exc.code = 1
#     raise


class FugitErrorMixin:
    """A mixin class for common functionality shared by all Fugit-specific errors.

    Attributes:
        message: A message describing the error.
        code: An optional error code from FugitErrorCodes enum.
    """

    def __init__(self, message: str, *, code: FugitErrorCodes | None) -> None:
        self.message = message
        self.code = code

    def __str__(self) -> str:
        if self.code is None:
            return self.message
        else:
            return f"{self.message}\n\nFor further information visit {ERROR_DOCS_URL}{self.code}"


class FugitUserError(FugitErrorMixin, TypeError):
    """An error raised due to incorrect use of Fugit."""


class FugitMisconfigurationExit(SystemExit):
    """
    An error raised due to incorrect Fugit CLI configuration.

    Attributes:
        code: The exit code for the shell (always 1).
    """

    def __init__(self) -> None:
        self.code = 1
