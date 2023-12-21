from contextlib import AbstractContextManager
from types import TracebackType

from .errors import FugitMisconfigurationExit
from .pipes import pipe_cleanup

__all__ = ("SuppressBrokenPipeError", "CaptureInvalidConfigExit")


class SuppressBrokenPipeError(AbstractContextManager):
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        if exc_type is BrokenPipeError:
            return pipe_cleanup()
        else:
            return super().__exit__(exc_type, exc_value, traceback)


class CaptureInvalidConfigExit(AbstractContextManager):
    def __exit__(
        self,
        exc_type: type[SystemExit] | None,
        exc_value: SystemExit | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        if exc_type is SystemExit and exc_value.code != 0:
            raise FugitMisconfigurationExit()
        else:
            # Do not intercept the SystemExit if CLI was passed `-h`
            return super().__exit__(exc_type, exc_value, traceback)
