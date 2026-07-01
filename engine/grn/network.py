from math import exp


class GRNNetwork:

    def __init__(self, genes, connections):

        self.genes = genes
        self.connections = connections

    def sigmoid(self, x):

        return 1 / (1 + exp(-x))

    def step(self, external_inputs):

        for gene in self.genes.values():

            gene.decay_expression()

        new_values = {}

        for name, gene in self.genes.items():

            total = external_inputs.get(name, 0.0)

            for connection in gene.incoming:

                if connection.enabled:

                    total += (
                        connection.source.expression
                        * connection.weight
                    )

            new_values[name] = self.sigmoid(total)

        for name, value in new_values.items():

            self.genes[name].previous_expression = (
                self.genes[name].expression
            )

            self.genes[name].expression = value