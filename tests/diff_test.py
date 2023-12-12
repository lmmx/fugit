from pytest import mark

from fugit import diff
from fugit.interfaces import DiffConfig


@mark.parametrize("config_cls", [DiffConfig, dict])
@mark.parametrize("expected", [[]])
def test_diff_output(config_cls, expected):
    config = config_cls()
    result = diff(config)
    assert result == expected
