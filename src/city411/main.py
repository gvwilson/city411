"""Synthesize data."""

import argparse
import json
import random
import sys

from faker import Faker

from .parameters import Parameters
from .person import Person


def main():
    """Main command-line driver."""

    args = _parse_args()
    if args.defaults:
        print(Parameters().as_json())
        return 0

    params = _initialize(args)

    fake = Faker(params.locale)
    data = {
        "persons": Person.make(params, fake)
    }

    return 0


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
