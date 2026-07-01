import csv
from pathlib import Path


class ExperimentReader:

    def load(

        self,

        experiment

    ):

        file = (

            Path("experiments")

            /

            experiment

            /

            "transition_log.csv"

        )

        with open(file) as f:

            rows = list(

                csv.DictReader(f)

            )

        if not rows:
            raise ValueError(
                f"No data rows found in {file}"
            )

        return rows[-1]