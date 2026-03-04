"""Data generation parameters."""

from dataclasses import dataclass
from datetime import date, timedelta
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

    def __post_init__(self):
        """Validate fields."""
        pass

    def as_json(self, indent=JSON_INDENT):
        """Convert parameters to a JSON string."""
        return json.dumps(self.__dict__, indent=indent, default=_serialize_json)


def _serialize_json(obj):
    """Custom JSON serializer."""
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    assert isinstance(obj, date)
    return obj.isoformat()
