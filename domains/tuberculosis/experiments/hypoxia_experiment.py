from domains.tuberculosis.experiments.base_experiment import BaseExperiment


class HypoxiaExperiment(BaseExperiment):

    def __init__(self):

        super().__init__()

        self.name = "Hypoxia"

        self.parameters["oxygen"] = 0.25