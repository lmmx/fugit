from math import copysign

from pydantic import RootModel, model_validator

__all__ = ("SignedInteger",)


class SignedInteger(RootModel):
    root: float

    @property
    def is_positive(self) -> bool:
        return copysign(1, self.root) > 0

    def __repr__(self) -> str:
        return f"{self.root:.0f}"

    def __eq__(self, other) -> bool:
        if self.root == other == 0:
            return copysign(1, self.root) == copysign(1, other)
        else:
            return self.root == other

    def __lt__(self, other) -> bool:
        if self.root == other == 0:
            # May be sign difference, compare bit representations
            return copysign(1, self.root) < copysign(1, other)
        else:
            return self.root < other

    def __gt__(self, other) -> bool:
        return not self < other

    @model_validator(mode="after")
    def check_integrity(self):
        assert self.root.is_integer()
