class TBMetabolism:

    def __init__(self):

        self.atp = 1.0

        self.redox = 0.5

        self.cell_health = 1.0

    def update(self, grn, inputs):

        self.atp += (

            0.10 * grn.functions["growth"]

            - 0.10 * (1 - inputs["oxygen"])

        )

        self.atp = max(
            0.0,
            min(1.0, self.atp)
        )

        self.redox += (

            0.05 * grn.regulators["whiB3"]

            - 0.03 * inputs["drug"]

        )

        self.redox = max(
            0.0,
            min(1.0, self.redox)
        )