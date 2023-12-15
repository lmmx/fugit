from __future__ import annotations

from parse import with_pattern
from parse_type import TypeBuilder

__all__ = ("parse_str", "SmolStrTypeBuilder", "parse_any_width_string")


@with_pattern(r".*")
def parse_str(text: str) -> str:
    """Optional string match regex helper"""
    return text


class SmolStrTypeBuilder(TypeBuilder):
    @classmethod
    def with_zero_or_more_chars(cls, converter, pattern=None):
        nullable_optional = cls.with_zero_or_one(converter=converter, pattern=pattern)

        @with_pattern(nullable_optional.pattern)
        def convert_optional(text, m=None):
            """Uses the empty string as the sentinel instead of `None`."""
            return converter(text) if text else ""

        convert_optional.regex_group_count = nullable_optional.regex_group_count
        return convert_optional


parse_any_width_string = SmolStrTypeBuilder.with_zero_or_more_chars(parse_str)
