from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    computed_field,
)

__all__ = ("DiffInfoPG2",)


class DiffFile(BaseModel):
    flags: int
    id: Annotated[str, BeforeValidator(str)]  # hex string coerced from `Oid` class
    mode: int
    path: str
    raw_path: str
    size: int


class DiffDelta(BaseModel):
    flags: int
    is_binary: bool
    new_file: DiffFile
    nfiles: int
    old_file: DiffFile
    similarity: int
    status: int
    status_char: Annotated[str, BeforeValidator(lambda method: method.__call__())]


class DiffLine(BaseModel):
    content: str
    content_offset: int
    new_lineno: int
    num_lines: int
    old_lineno: int
    origin: Literal[" ", "-", "+"]  # Alternatively use to discriminate union
    raw_content: bytes


class DiffHunk(BaseModel):
    new_start: int
    new_lines: int
    old_start: int
    old_lines: int
    header: str  # This might be a string that represents the hunk header
    # Including lines might require another model if they have a complex structure
    lines: list[DiffLine]


class DiffPatch(BaseModel):
    delta: DiffDelta
    hunks: list[DiffHunk]
    line_stats: tuple[int, int, int] = Field(repr=False, exclude=True)
    text: str

    @computed_field
    @property
    def context(self) -> int:
        return self.line_stats[0]

    @computed_field
    @property
    def additions(self) -> int:
        return self.line_stats[1]

    @computed_field
    @property
    def deletions(self) -> int:
        return self.line_stats[2]


class DiffInfoPG2(DiffPatch):
    @property
    def change_type(self) -> str:
        return self.delta.status_char

    @property
    def paths_repr(self) -> str:
        """Join a and b paths, in order, with '->' if they differ, else just give one"""
        ap, bp = (f.path for f in (self.delta.old_file, self.delta.new_file))
        unique_paths = dict.fromkeys([ap, bp])
        return "{}".format(" -> ".join(unique_paths))

    @property
    def overview(self) -> str:
        return f"{self.change_type}: {self.paths_repr}\n"
