"""Discrete-event simulation process for a single person."""

import random

import asimpy

from .call import Call, Conversation


class PersonProcess(asimpy.Process):
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
