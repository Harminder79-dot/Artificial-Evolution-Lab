import json
from pathlib import Path


class ConfigLoader:

    def __init__(self, domain, config):

        folder = Path(__file__).parent / domain

        baseline = folder / "baseline.json"

        with open(baseline, "r") as f:
            self.data = json.load(f)

        if config != "baseline":

            override = folder / f"{config}.json"

            with open(override, "r") as f:
                update = json.load(f)

            self.merge(self.data, update)

    def merge(self, base, update):

        for key, value in update.items():

            if isinstance(value, dict):

                if key not in base:
                    base[key] = {}

                self.merge(base[key], value)

            else:

                base[key] = value

    def __getitem__(self, key):

        return self.data[key]