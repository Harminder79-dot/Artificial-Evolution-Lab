import random


class TBGRN:

    def __init__(self):

        self.oxygen = 1.0

        self.genes = {

            "dosR": 0.0,
            "growth": 1.0,
            "stress": 0.0

        }

    def update(self, oxygen):

        self.oxygen = oxygen

        self.genes["dosR"] *= 0.95
        self.genes["growth"] *= 0.95
        self.genes["stress"] *= 0.95

        self.genes["dosR"] += (1 - oxygen) * 0.05
        self.genes["growth"] += oxygen * 0.03
        self.genes["stress"] += abs(0.5 - oxygen) * 0.02

        for gene in self.genes:

            self.genes[gene] = max(
                0,
                min(
                    1,
                    self.genes[gene]
                )
            )

    def dominant_state(self):

        if self.genes["dosR"] > 0.65:
            return "DORMANT"

        if 0.30 < self.oxygen < 0.60:
            return "STRESSED"

        return "ACTIVE"