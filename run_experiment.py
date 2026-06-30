import subprocess
import sys

EXPERIMENTS = [

    "baseline",

    "hypoxia",

    "hyperoxia",

    "treatment",

    "immune_high"

]


def run(experiment):

    print(f"\nRunning {experiment}")

    result = subprocess.run(

        [

            sys.executable,

            "main_tb.py",

            experiment

        ]

    )

    if result.returncode == 0:

        print(

            f"{experiment} completed."

        )

    else:

        print(

            f"{experiment} failed."

        )


if __name__ == "__main__":

    for experiment in EXPERIMENTS:

        run(experiment)