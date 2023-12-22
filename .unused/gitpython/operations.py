from __future__ import annotations

from git import IndexFile

from ....interfaces import DiffConfig
from .structures import DiffInfoGP

__all__ = ("get_diff", "count_match", "discard_diff_type")


def get_diff(index: IndexFile, tree: str | None, create_patch: bool):
    """
    Don't pass a tree in directly, allow it to be handled by GitPython.
    It seems the reverse diff is given when the tree is any str except None
    so reverse it with the R kwarg if anything else is passed as `tree`.
    https://github.com/gitpython-developers/GitPython/issues/852
    """
    reverse = tree is not None
    return index.diff(tree, create_patch=create_patch, R=reverse)


def discard_diff_type(diff_info: DiffInfoGP, config: DiffConfig) -> bool:
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
