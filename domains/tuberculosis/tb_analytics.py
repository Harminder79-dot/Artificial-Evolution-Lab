#we're separating Simulation from Analysis
class TBAnalytics:

    def __init__(self):

        self.history = {

            "population": [],

            "avg_dosR": [],

            "avg_sigH": [],

            "avg_sigE": [],

            "avg_growth": [],

            "avg_atp": [],

            "avg_redox": [],

            "avg_health": []

        }

    def record(self, world):

        bacteria = world.bacteria

        if len(bacteria) == 0:

            return

        N = len(bacteria)

        self.history["population"].append(N)

        self.history["avg_dosR"].append(

            sum(
                b.grn.regulators["dosR"]
                for b in bacteria
            ) / N
        )

        self.history["avg_sigH"].append(

            sum(
                b.grn.regulators["sigH"]
                for b in bacteria
            ) / N
        )

        self.history["avg_sigE"].append(

            sum(
                b.grn.regulators["sigE"]
                for b in bacteria
            ) / N
        )

        self.history["avg_growth"].append(

            sum(
                b.grn.functions["growth"]
                for b in bacteria
            ) / N
        )

        self.history["avg_atp"].append(

            sum(
                b.metabolism.atp
                for b in bacteria
            ) / N
        )

        self.history["avg_redox"].append(

            sum(
                b.metabolism.redox
                for b in bacteria
            ) / N
        )

        self.history["avg_health"].append(

            sum(
                b.metabolism.cell_health
                for b in bacteria
            ) / N
        )