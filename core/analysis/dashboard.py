from core.experiment.experiment_reader import ExperimentReader
from domains.tuberculosis.rule_validator import RuleValidator


class Dashboard:

    def __init__(self):

        self.reader = ExperimentReader()

        self.validator = RuleValidator()

    def run(self):

        baseline = self.reader.load("baseline")

        experiments = [

            "hypoxia",

            "hyperoxia",

            "treatment",

            "immune_high"

        ]

        for experiment in experiments:

            print()

            print("=" * 60)

            print(experiment.upper())

            print("=" * 60)

            data = self.reader.load(experiment)

            self.validator.validate(

                baseline,

                data,

                experiment

            )