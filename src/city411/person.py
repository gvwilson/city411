"""Persons."""

from dataclasses import dataclass, field
from datetime import timedelta
import math
import random

from ._utils import id_generator, validate


_NEXT_ID = id_generator("P", 4)
_LOGNORMAL_SIGMA = 1.0


@dataclass
class Person:
    """A single person."""

    ident: str = ""
    """Unique identifier (constructed internally)."""

    family: str = ""
    """Family name."""

    personal: str = ""
    """Personal name."""

    mean_call_interval: timedelta = field(default_factory=lambda: timedelta(0))
    """Mean time between call clusters for this person."""

    def __post_init__(self):
        """Validate fields and generate unique identifier."""

        validate(self.ident == "", "person ID cannot be set externally")
        validate(len(self.family) > 0, "family name cannot be empty")
        validate(len(self.personal) > 0, "personal name cannot be empty")
        validate(self.mean_call_interval > timedelta(0), "mean call interval must be positive")

        self.ident = next(_NEXT_ID)

    @classmethod
    def make(cls, params, fake):
        """Construct multiple persons."""

        mu = math.log(params.mean_call_interval / timedelta(days=1))
        return [
            cls(
                family=fake.last_name(),
                personal=fake.first_name(),
                mean_call_interval=timedelta(days=random.lognormvariate(mu, _LOGNORMAL_SIGMA)),
            )
            for _ in range(params.num_persons)
        ]
