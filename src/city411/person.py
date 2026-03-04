"""Persons."""

from dataclasses import dataclass
import random

from ._utils import id_generator, validate


_NEXT_ID = id_generator("P", 4)


@dataclass
class Person:
    """A single person."""

    ident: str = ""
    """Unique identifier (constructed internally)."""

    family: str = ""
    """Family name."""

    personal: str = ""
    """Personal name."""

    def __post_init__(self):
        """Validate fields and generate unique identifier."""

        validate(self.ident == "", "person ID cannot be set externally")
        validate(len(self.family) > 0, "family name cannot be empty")
        validate(len(self.personal) > 0, "personal name cannot be empty")

        self.ident = next(_NEXT_ID)

    @classmethod
    def make(cls, params, fake):
        """Construct multiple persons."""

        return [
            cls(
                family=fake.last_name(),
                personal=fake.first_name(),
            )
            for _ in range(params.num_persons)
        ]
