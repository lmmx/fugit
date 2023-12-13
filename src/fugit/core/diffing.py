from git import IndexFile, Repo, Tree
from pydantic import BaseModel, ConfigDict

from ..interfaces import DiffConfig

__all__ = ["get_diff", "load_diff_info", "diff"]


def get_diff(index: IndexFile, tree: str | None, create_patch: bool):
    """
    Don't pass a tree in directly, allow it to be handled by GitPython.
    It seems the reverse diff is given when the tree is any str except None
    so reverse it with the R kwarg if anything else is passed as `tree`.
    https://github.com/gitpython-developers/GitPython/issues/852
    """
    reverse = tree is not None
    return index.diff(tree, create_patch=create_patch, R=reverse)


def filter_diff(patch, info, config: DiffConfig) -> list[str]:
    """
    Filter file-level diffs using info from both patch and metadata diffs.
    """
    # Do any further filtering logic here
    diff_text = patch.diff.decode()
    print(diff_text)
    return [diff_text]


def count_match(patches, infos) -> None:
    """Confirm diff sequences are same cardinality before zipping them together."""
    if (pc := len(patches)) != (ic := len(infos)):
        raise ValueError(f"Diff mismatch: {pc} != {ic}")


def load_diff(config: DiffConfig) -> list[str]:
    # Note: You can either implement commit tree-based diffs (with less reversal
    # weirdness) or get it from a string at runtime (more configurable so we do that)
    # tree = repo.head.commit.tree
    repo = Repo(config.repo, search_parent_directories=True)
    index = repo.index
    tree = config.revision
    file_diff_patch = get_diff(index, tree, create_patch=True)
    file_diff_info = get_diff(index, tree, create_patch=False)
    count_match(file_diff_patch, file_diff_info)
    diffs = []
    for diff_patch, diff_info in zip(file_diff_patch, file_diff_info):
        filtered = filter_diff(patch=diff_patch, info=diff_info, config=config)
        diffs.extend(filtered)
    return diffs


def diff(config: dict | DiffConfig) -> list[str]:
    """Narrow the input type to DiffConfig type for `load_diff`."""
    return load_diff(DiffConfig.model_validate(config))
