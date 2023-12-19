from __future__ import annotations

from typing import Any, Literal

from git import Diff
from git.objects.blob import Blob
from pydantic import BaseModel, ConfigDict, computed_field, create_model

__all__ = (
    "SrcInfo",
    "DstInfo",
    "PatchedMetadata",
    "PatchlessMetadata",
    "DeltaInfo",
    "DiffInfo",
)


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
