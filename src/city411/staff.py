"""Call center staff and call handling simulation."""

import asimpy
from dataclasses import dataclass
from datetime import timedelta
import math
import random

from ._utils import id_generator, validate


_NEXT_STAFF_ID = id_generator("S", 4)
_LOGNORMAL_SIGMA = 1.0

WORK_START_HOUR = 9
WORK_END_HOUR = 17


@dataclass
class Staff:
    """A single call center staff member."""

    ident: str = ""
    """Unique identifier (constructed internally)."""

    family: str = ""
    """Family name."""

    personal: str = ""
    """Personal name."""

    role: str = ""
    """Role: 'frontline' or 'supervisor'."""

    def __post_init__(self):
        validate(self.ident == "", "staff ID cannot be set externally")
        validate(len(self.family) > 0, "family name cannot be empty")
        validate(len(self.personal) > 0, "personal name cannot be empty")
        validate(self.role in ("frontline", "supervisor"), f"unknown role '{self.role}'")
        self.ident = next(_NEXT_STAFF_ID)

    @classmethod
    def make(cls, params, fake):
        """Construct frontline staff and supervisors."""
        frontline = [
            cls(family=fake.last_name(), personal=fake.first_name(), role="frontline")
            for _ in range(params.num_frontline_staff)
        ]
        supervisors = [
            cls(family=fake.last_name(), personal=fake.first_name(), role="supervisor")
            for _ in range(params.num_supervisors)
        ]
        return frontline + supervisors


def _secs_until_shift_start(start_date, sim_now):
    """Return seconds until the next shift begins (0 if currently in a shift)."""
    dt = start_date + timedelta(seconds=int(sim_now))
    if dt.weekday() < 5 and WORK_START_HOUR <= dt.hour < WORK_END_HOUR:
        return 0.0
    if dt.weekday() < 5 and dt.hour < WORK_START_HOUR:
        next_start = dt.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
    else:
        next_day = dt + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        next_start = next_day.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
    return (next_start - dt).total_seconds()


def _secs_until_shift_end(start_date, sim_now):
    """Return seconds until the current shift ends."""
    dt = start_date + timedelta(seconds=int(sim_now))
    end = dt.replace(hour=WORK_END_HOUR, minute=0, second=0, microsecond=0)
    return (end - dt).total_seconds()


class StaffProcess(asimpy.Process):
    """Simulates one staff member handling calls during working hours."""

    def init(self, staff, params, call_queue, escalation_queue):
        self.staff = staff
        self.params = params
        self.call_queue = call_queue
        self.escalation_queue = escalation_queue

    async def run(self):
        is_supervisor = self.staff.role == "supervisor"
        queue = self.escalation_queue if is_supervisor else self.call_queue
        mean_duration = (
            self.params.mean_escalation_duration
            if is_supervisor
            else self.params.mean_call_duration
        )
        mu = math.log(mean_duration.total_seconds())
        end_time = (self.params.end_date - self.params.start_date).total_seconds()

        while self.now < end_time:
            # Outer loop: wait until the next shift starts.
            wait = _secs_until_shift_start(self.params.start_date, self.now)
            if wait > 0:
                await self.timeout(wait)
            if self.now >= end_time:
                break

            # Inner loop: handle calls until the shift ends.
            while True:
                remaining = _secs_until_shift_end(self.params.start_date, self.now)
                if remaining <= 0:
                    break

                which, call = await asimpy.FirstOf(
                    self._env,
                    call=queue.get(),
                    shift_end=self._env.timeout(remaining),
                )
                if which == "shift_end":
                    break

                duration = random.lognormvariate(mu, _LOGNORMAL_SIGMA)

                if is_supervisor:
                    call.escalation_wait_time = self.now - call.escalation_time
                    call.supervisor_id = self.staff.ident
                    await self.timeout(duration)
                    call.escalation_handle_time = duration
                else:
                    call.staff_id = self.staff.ident
                    call.wait_time = self.now - call.time
                    await self.timeout(duration)
                    call.handle_time = duration
                    if random.random() < self.params.p_escalation:
                        call.escalated = True
                        call.escalation_time = self.now
                        await self.escalation_queue.put(call)
