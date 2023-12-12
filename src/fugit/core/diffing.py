from ..interfaces import DiffConfig

__all__ = ["diff"]


def diff(config: dict | DiffConfig) -> list[str]:
    config: DiffConfig = DiffConfig.adapt(config)  # Narrow the type
    print(repr(config))
    diffs = []
    return diffs
