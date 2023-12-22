from __future__ import annotations

from enum import Enum, IntEnum
from typing import Literal

from msgspec import Struct

__all__ = ("DiffInfoPG2",)


class DiffFile(Struct):
    # flags: int
    # id: Annotated[str, BeforeValidator(str)]  # hex string coerced from `Oid` class
    # mode: int
    path: str
    # raw_path: str
    # size: int


class GitDeltaStatus(Enum):
    UNMODIFIED = ""  # This one is not defined, I added it
    ADDED = "A"
    DELETED = "D"
    MODIFIED = "M"
    RENAMED = "R"
    COPIED = "C"
    IGNORED = "I"
    UNTRACKED = "?"
    TYPECHANGE = "T"
    UNREADABLE = "X"
    UNKNOWN = " "

    @staticmethod
    def from_status(status: str) -> GitDeltaStatus:
        for name, member in GitDeltaStatus.__members__.items():
            if member.value == status:
                return member
        return GitDeltaStatus.UNKNOWN


class DeltaStatus(IntEnum):
    """
    Taken directly from pygit2 (`diff.h`).
    """

    UNMODIFIED = 0
    ADDED = 1  # A
    DELETED = 2  # D
    MODIFIED = 3  # M
    RENAMED = 4  # R
    COPIED = 5  # C
    IGNORED = 6
    UNTRACKED = 7
    TYPECHANGE = 8
    UNREADABLE = 9
    CONFLICTED = 10


class DiffDelta(Struct):
    # flags: int
    # is_binary: bool
    new_file: DiffFile
    # nfiles: int
    old_file: DiffFile
    # similarity: int
    status: DeltaStatus
    # status_char: str  # Annotated[str, BeforeValidator(lambda method: method.__call__())]


class DiffLine(Struct):
    content: str
    content_offset: int
    new_lineno: int
    num_lines: int
    old_lineno: int
    origin: Literal[" ", "-", "+"]  # Alternatively use to discriminate union
    # raw_content: bytes


class DiffHunk(Struct):
    # new_start: int
    # new_lines: int
    # old_start: int
    # old_lines: int
    header: str  # This might be a string that represents the hunk header
    # Including lines might require another model if they have a complex structure
    lines: list[DiffLine]


class DiffPatch(Struct):
    delta: DiffDelta
    hunks: list[DiffHunk]
    text: str
    # line_stats: tuple[int, int, int] = Field(repr=False, exclude=True)

    # @computed_field
    # @property
    # def context(self) -> int:
    #     return self.line_stats[0]

    # @computed_field
    # @property
    # def additions(self) -> int:
    #     return self.line_stats[1]

    # @computed_field
    # @property
    # def deletions(self) -> int:
    #     return self.line_stats[2]


class DiffInfoPG2(DiffPatch):
    @property
    def change_type(self) -> str:
        return GitDeltaStatus[self.delta.status.name].value

    @property
    def paths_repr(self) -> str:
        """Join a and b paths, in order, with '->' if they differ, else just give one"""
        ap, bp = (f.path for f in (self.delta.old_file, self.delta.new_file))
        unique_paths = dict.fromkeys([ap, bp])
        return "{}".format(" -> ".join(unique_paths))

    @property
    def overview(self) -> str:
        return f"{self.change_type}: {self.paths_repr}\n"
