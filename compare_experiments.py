from core.experiment.experiment_reader import ExperimentReader
from domains.tuberculosis.rule_validator import RuleValidator
from core.analysis.comparator import Comparator
import sys

reader = ExperimentReader()

if len(sys.argv) != 3:

    print("Usage:")

    print("python compare_experiments.py baseline hypoxia")

    sys.exit()

baseline_name = sys.argv[1]

experiment_name = sys.argv[2]

baseline = reader.load(

    baseline_name

)

experiment = reader.load(

    experiment_name

)

Comparator.compare(
    baseline,
    experiment,
    experiment_name
)

validator = RuleValidator()

validator.validate(
    baseline,
    experiment,
    experiment_name
)