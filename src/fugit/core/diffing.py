from git import Repo
from pydantic import BaseModel, ConfigDict

from ..interfaces import DiffConfig

__all__ = ["diff"]


def load_diff_info(repo: Repo) -> list[str]:
    staged_diff_patch = repo.index.diff("HEAD", create_patch=True)
    staged_diff_info = repo.index.diff("HEAD", create_patch=False)
    # assert len(staged_diff_info) == len(staged_diff_patch) == 57
    # for file_diff_patch, file_diff_info in zip(staged_diff_patch, staged_diff_info):
    #     diff_text = file_diff_patch.diff.decode()
    #     print(diff_text)
    #     breakpoint()
    #     diff_lines = diff_text.splitlines()
    return []


def diff(config: dict | DiffConfig) -> list[str]:
    config: DiffConfig = DiffConfig.model_validate(config)  # Narrow the type
    repo = Repo(config.repo)
    diffs = load_diff_info(repo)
    return diffs
