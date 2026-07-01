from domains.tuberculosis.experiments.base_experiment import BaseExperiment


class DrugExperiment(BaseExperiment):

    def __init__(self):

        super().__init__()

        self.name = "Drug"

        self.parameters["drug"] = True