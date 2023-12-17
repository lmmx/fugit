from __future__ import annotations

from typing import Any, Literal

from git import Diff, IndexFile, Repo
from git.objects.blob import Blob
from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    computed_field,
    create_model,
)
from rich.text import Text

from ..interfaces import DiffConfig
from .io import fugit_console

__all__ = ("get_diff", "discard_diff", "count_match", "load_diff", "diff")


def get_diff(index: IndexFile, tree: str | None, create_patch: bool):
    """
    Don't pass a tree in directly, allow it to be handled by GitPython.
    It seems the reverse diff is given when the tree is any str except None
    so reverse it with the R kwarg if anything else is passed as `tree`.
    https://github.com/gitpython-developers/GitPython/issues/852
    """
    reverse = tree is not None
    return index.diff(tree, create_patch=create_patch, R=reverse)


def prefixed_model(prefix: str, field_types: list[tuple[str, Any]], /) -> dict:
    """Make kwargs for `pydantic.create_model`, applying a prefix to a field schema."""
    fields = {f"{prefix}_{field}": (typ | None, ...) for field, typ in field_types}
    return {"__config__": ConfigDict(arbitrary_types_allowed=True), **fields}


field_types = [("blob", Blob), ("mode", int), ("rawpath", bytes)]
SrcInfo = create_model("SrcInfo", **prefixed_model("a", field_types))
DstInfo = create_model("DstInfo", **prefixed_model("b", field_types))


class PatchedMetadata(BaseModel):
    diff: bytes


class PatchlessMetadata(BaseModel):
    change_type: Literal["A", "D", "C", "M", "R", "T", "U"]
    raw_rename_from: bytes | None
    raw_rename_to: bytes | None
    copied_file: bool
    deleted_file: bool
    new_file: bool


class DeltaInfo(DstInfo, SrcInfo):
    """
    The combination of Src and Dst models, available from GitPython with/out diff patch.
    """


class DiffInfo(DeltaInfo, PatchlessMetadata, PatchedMetadata):
    @computed_field
    @property
    def paths_repr(self) -> str:
        """Join a and b paths, in order, with '->' if they differ, else just give one"""
        ap, bp = self.a_rawpath, self.b_rawpath
        unique_paths = dict.fromkeys(filter(None, [ap, bp]))
        return "{}".format(" -> ".join(map(bytes.decode, unique_paths)))

    @computed_field
    @property
    def overview(self) -> str:
        return f"{self.change_type}: {self.paths_repr}\n"

    @computed_field(repr=False)
    @property
    def text(self) -> str:
        return self.diff.decode()

    @classmethod
    def from_tree_pair(cls, *, patch: Diff, info: Diff) -> DiffInfo:
        """Instantiate from GitPython's patched and unpatched tree diffs."""
        delta_info = DeltaInfo.model_validate(patch, from_attributes=True)
        patched = PatchedMetadata.model_validate(patch, from_attributes=True)
        no_patch = PatchlessMetadata.model_validate(info, from_attributes=True)
        merged = {
            **delta_info.model_dump(),
            **patched.model_dump(),
            **no_patch.model_dump(),
        }
        return DiffInfo.model_validate(merged)


def discard_diff(diff_info: DiffInfo, config: DiffConfig) -> bool:
    """
    Filter file-level diffs using info from both patch and metadata diffs.
    Returns a boolean indicating whether the filter config captures or rejects the diff.
    """
    rejected = diff_info.change_type not in config.change_type
    return rejected


def count_match(patches, infos) -> None:
    """Confirm diff sequences are same cardinality before zipping them together."""
    if (pc := len(patches)) != (ic := len(infos)):
        raise ValueError(f"Diff mismatch: {pc} != {ic}")


def highlight_diff(diff: str) -> None:
    """This replaces the highlighter applied by `Console.render_markup`."""
    # TODO express this as a Rich highlighter class
    highlight_patterns = {
        "removed": (r"^\+.*", "green"),
        "added": (r"^-.*", "red"),
        "hunk_context": (r"^@@.*", "bold white"),  # applied first (whole line)
        "hunk_header": (r"^@@.*?@@ ", "blue"),  # applied second (only inside @ signs)
    }
    diff_lines = Text(style="white")
    for line in diff.splitlines(keepends=True):
        diff_line = Text(line)
        for pattern, style in highlight_patterns.values():
            diff_line.highlight_regex(pattern, style=style)
        diff_lines.append_text(diff_line)
    return diff_lines


def load_diff(config: DiffConfig) -> list[str]:
    """
    Note: You can either implement commit tree-based diffs (with no 'R' kwarg reversal
    weirdness) or get it from a string at runtime (more configurable so we do that).
    For reference, you would do it like this rather than ``config.revision``:

      >>> tree = repo.head.commit.tree
    """
    repo = Repo(config.repo, search_parent_directories=True)
    index = repo.index
    tree = config.revision
    file_diff_patch = get_diff(index, tree, create_patch=True)
    file_diff_info = get_diff(index, tree, create_patch=False)
    count_match(file_diff_patch, file_diff_info)
    diffs: list[str] = []
    with fugit_console.pager_available() as console:
        for patch, info in zip(file_diff_patch, file_diff_info):
            try:
                diff_info = DiffInfo.from_tree_pair(patch=patch, info=info)
            except ValidationError:
                raise  # TODO: make a nicer custom error and exit
            if discard_diff(diff_info=diff_info, config=config):
                continue
            filtrate = diff_info.text
            diffs.append(filtrate)
            console.print(diff_info.overview, style="bold yellow underline")
            # This simulates the render process (`Console.render_str`)
            rendered_filtrate = highlight_diff(filtrate)
            console.print(rendered_filtrate)
            console.file_count += 1
            del diff_info
    return diffs


def diff(**config) -> list[str]:
    """Narrow the input type to DiffConfig type for `load_diff`."""
    return load_diff(DiffConfig.model_validate(config))
