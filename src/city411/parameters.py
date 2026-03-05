"""Data generation parameters."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
from faker.config import AVAILABLE_LOCALES


# Indentation for JSON output.
JSON_INDENT = 2


@dataclass
class Parameters:
    """Store all data generation parameters."""

    seed: int = 12345
    """Random number generator seed for reproducible data generation."""

    locale: str = "en_CA"
    """Locale for generating people and locations."""

    num_persons: int = 20
    """Number of persons."""

    mean_call_interval: timedelta = timedelta(days=30)
    """Median mean time between call clusters across persons."""

    mean_calls_per_conversation: float = 3.0
    """Mean number of calls per conversation (geometric distribution)."""

    mean_followup_interval: timedelta = timedelta(days=2)
    """Mean time between follow-up calls within a conversation."""

    start_date: datetime = datetime(2024, 1, 1)
    """Start date of the simulation."""

    end_date: datetime = datetime(2024, 12, 31)
    """End date of the simulation."""

    def __post_init__(self):
        """Validate fields."""
        if self.end_date <= self.start_date:
            raise ValueError(f"end_date {self.end_date} must be after start_date {self.start_date}")

    def as_json(self, indent=JSON_INDENT):
        """Convert parameters to a JSON string."""
        return json.dumps(self.__dict__, indent=indent, default=_serialize_json)


def _serialize_json(obj):
    """Custom JSON serializer."""
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"cannot serialize {type(obj)}")
