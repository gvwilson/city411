"""Calls and conversations."""

from dataclasses import dataclass, field

from ._utils import id_generator


_NEXT_CONVERSATION_ID = id_generator("C", 6)
_NEXT_CALL_ID = id_generator("K", 6)


@dataclass
class Call:
    """A single call from a person to the city."""

    ident: str = ""
    """Unique identifier (constructed internally)."""

    conversation_id: str = ""
    """ID of the conversation this call belongs to."""

    person_id: str = ""
    """ID of the person who made this call."""

    time: float = 0.0
    """Simulation time when the call was made."""

    sequence: int = 0
    """Position of this call within its conversation (1-based)."""

    def __post_init__(self):
        self.ident = next(_NEXT_CALL_ID)


@dataclass
class Conversation:
    """A sequence of related calls from a person."""

    ident: str = ""
    """Unique identifier (constructed internally)."""

    person_id: str = ""
    """ID of the person who initiated this conversation."""

    start_time: float = 0.0
    """Simulation time when the conversation started."""

    calls: list = field(default_factory=list)
    """Calls made in this conversation, in order."""

    def __post_init__(self):
        self.ident = next(_NEXT_CONVERSATION_ID)
