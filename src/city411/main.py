"""Synthesize data."""

import argparse
from datetime import timedelta
import json
import random
import sys

import asimpy
from faker import Faker
import polars as pl

from .parameters import Parameters
from .person import Person
from .person_process import PersonProcess


def main():
    """Main command-line driver."""

    args = _parse_args()
    if args.defaults:
        print(Parameters().as_json())
        return 0

    params = _initialize(args)
    fake = Faker(params.locale)
    persons = Person.make(params, fake)
    df = _simulate(params, persons)

    for key, frame in df.items():
        print(key)
        print(frame)

    return 0


def _simulate(params, persons):
    results = {"conversations": [], "calls": []}
    env = asimpy.Environment()
    for person in persons:
        PersonProcess(env, person, params, results)
    env.run(until=(params.end_date - params.start_date).total_seconds())
    return _to_dataframes(params, persons, results)


def _to_dataframes(params, persons, results):
    """Convert simulation results to Polars dataframes."""

    def to_ts(seconds):
        return params.start_date + timedelta(seconds=seconds)

    persons_df = pl.DataFrame([
        {"ident": p.ident, "family": p.family, "personal": p.personal}
        for p in persons
    ])

    conversations_df = pl.DataFrame([
        {"ident": c.ident, "person_id": c.person_id, "start_time": to_ts(c.start_time)}
        for c in results["conversations"]
    ])

    calls_df = pl.DataFrame([
        {"ident": c.ident, "conversation_id": c.conversation_id, "person_id": c.person_id, "time": to_ts(c.time), "sequence": c.sequence}
        for c in results["calls"]
    ])

    return {"persons": persons_df, "conversations": conversations_df, "calls": calls_df}


def _initialize(args):
    """Initialize for data synthesis."""

    if args.params:
        with open(args.params, "r") as reader:
            params = Parameters(**json.load(reader))
    else:
        params = Parameters()

    for ov in args.override:
        fields = ov.split("=")
        assert len(fields) == 2, f"malformed override {ov}"
        key, value = fields
        assert hasattr(params, key), f"unknown override key {key}"
        prior = getattr(params, key)
        setattr(params, key, type(prior)(value))

    random.seed(params.seed)

    return params


def _parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--defaults", action="store_true", help="show default parameters"
    )
    parser.add_argument(
        "--override", default=[], nargs="+", help="name=value parameters"
    )
    parser.add_argument("--params", default=None, help="JSON parameter file")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
