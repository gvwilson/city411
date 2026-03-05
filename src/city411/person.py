"""Persons."""

from asimpy import Process
from dataclasses import dataclass, field
from datetime import timedelta
import math
import random

from .call import Call, Conversation
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
        validate(
            self.mean_call_interval > timedelta(0),
            "mean call interval must be positive",
        )

        self.ident = next(_NEXT_ID)

    @classmethod
    def make(cls, params, fake):
        """Construct multiple persons."""

        mu = math.log(params.mean_call_interval / timedelta(days=1))
        return [
            cls(
                family=fake.last_name(),
                personal=fake.first_name(),
                mean_call_interval=timedelta(
                    days=random.lognormvariate(mu, _LOGNORMAL_SIGMA)
                ),
            )
            for _ in range(params.num_persons)
        ]


class PersonProcess(Process):
    """Simulates one person's calls to the city over time."""

    def init(self, person, params, results):
        self.person = person
        self.params = params
        self.results = results

    async def run(self):
        p_resolve = 1.0 / self.params.mean_calls_per_conversation
        conv_interval = self.person.mean_call_interval.total_seconds()
        followup_interval = self.params.mean_followup_interval.total_seconds()
        end_time = (self.params.end_date - self.params.start_date).total_seconds()

        while self.now < end_time:
            # Outer loop: wait for the next conversation to start.
            await self.timeout(random.expovariate(1.0 / conv_interval))
            if self.now >= end_time:
                break

            conversation = Conversation(
                person_id=self.person.ident,
                start_time=self.now,
            )
            self.results["conversations"].append(conversation)

            # Inner loop: generate follow-up calls until the issue resolves.
            sequence = 1
            while True:
                call = Call(
                    conversation_id=conversation.ident,
                    person_id=self.person.ident,
                    time=self.now,
                    sequence=sequence,
                )
                conversation.calls.append(call)
                self.results["calls"].append(call)

                if random.random() < p_resolve:
                    break

                sequence += 1
                await self.timeout(random.expovariate(1.0 / followup_interval))
                if self.now >= end_time:
                    break
