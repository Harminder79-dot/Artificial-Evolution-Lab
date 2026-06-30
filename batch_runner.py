import subprocess
import sys


REPEATS = 5

EXPERIMENTS = [

    "baseline",

    "hypoxia",

    "hyperoxia",

    "treatment",

    "immune_high"

]


for experiment in EXPERIMENTS:

    for run in range(REPEATS):

        print(

            f"\n{experiment} "

            f"Run {run+1}/{REPEATS}"

        )

        subprocess.run(

            [

                sys.executable,

                "main_tb.py",

                experiment

            ]

        )