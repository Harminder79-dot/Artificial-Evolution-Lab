class TBObservables:

    def __init__(self):

        self.history = {

            "tick": [],

            "population": [],

            "active_fraction": [],

            "dormant_fraction": [],

            "stressed_fraction": [],

            "average_dosR": [], 

            "average_sigH": [],

            "average_sigE": [],

            "average_growth": [],

            "average_atp": [],

            "average_redox": [],

            "average_cell_health": [],

            "mdr_fraction": [],

            "xdr_fraction": [],

            "average_grn_weight": []
        }

    def record(self, world, ):

        bacteria = world.bacteria

        N = max(1, len(bacteria))

        # ---------------- Population ----------------

        active = sum(
            1 for b in bacteria
            if b.state == b.ACTIVE
        )

        dormant = sum(
            1 for b in bacteria
            if b.state == b.DORMANT
        )

        stressed = sum(
            1 for b in bacteria
            if b.state == b.STRESSED
        )

        # ---------------- Resistance ----------------

        mdr = sum(
            1 for b in bacteria
            if b.is_mdr
        )

        xdr = sum(
            1 for b in bacteria
            if b.is_xdr
        )

        # ---------------- Store History ----------------

        self.history["tick"].append(world.tick)

        self.history["population"].append(len(bacteria))

        self.history["active_fraction"].append(active / N)

        self.history["dormant_fraction"].append(dormant / N)

        self.history["stressed_fraction"].append(stressed / N)

        self.history["mdr_fraction"].append(mdr / N)

        self.history["xdr_fraction"].append(xdr / N)

        # ---------------- GRN ----------------

        self.history["average_dosR"].append(

            sum(
                b.grn.regulators["dosR"]
                for b in bacteria
            ) / N

        )

        self.history["average_sigH"].append(

            sum(
                b.grn.regulators["sigH"]
                for b in bacteria
            ) / N

        )

        self.history["average_sigE"].append(

            sum(
                b.grn.regulators["sigE"]
                for b in bacteria
            ) / N

        )

        self.history["average_growth"].append(

            sum(
                b.grn.functions["growth"]
                for b in bacteria
            ) / N

        )

        # ---------------- Metabolism ----------------

        self.history["average_atp"].append(

            sum(
                b.metabolism.atp
                for b in bacteria
            ) / N

        )

        self.history["average_redox"].append(

            sum(
                b.metabolism.redox
                for b in bacteria
            ) / N

        )

        self.history["average_cell_health"].append(

            sum(
                b.metabolism.cell_health
                for b in bacteria
            ) / N

        )

        weights = []

        for b in world.bacteria:

            for c in b.grn.connections:

                weights.append(c.weight)

        if weights:

            self.history["average_grn_weight"].append(

                sum(weights) / len(weights)

            )