from __future__ import annotations

from typing import Union

from .bases import Style, TextLine
from .escaping import esc_pair

__all__ = (
    "RedText",
    "GreenText",
    "BlueText",
    "WhiteText",
    "BoldWhiteText",
    "BoldYellow_Text",
    "SimpleLine",
    "PALETTE",
)


class RedText(TextLine):
    """red"""


class GreenText(TextLine):
    """green"""


class BlueText(TextLine):
    """blue"""


class WhiteText(TextLine):
    """white"""


class BoldWhiteText(TextLine):
    """bold white"""


class BoldYellow_Text(TextLine):
    """bold yellow underline"""


# Union of all the simple model types
SimpleLine = Union[
    RedText,
    GreenText,
    BlueText,
    WhiteText,
    BoldWhiteText,
    BoldYellow_Text,
]

# Test the Style Enum's completeness
# {'r': <class 'fugit.core.text.palette.RedText'>, ...
PALETTE = {Style(c.__doc__).name: esc_pair(c) for c in TextLine.__subclasses__()}
