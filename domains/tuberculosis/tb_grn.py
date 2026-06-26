import random
from domains.tuberculosis.tb_grn_network import REGULATORY_NETWORK
import math
from domains.tuberculosis.tb_parameters import TB_PARAMETERS

class TBGRN:

    def __init__(self, genome):

        # Store genome for later use
        self.genome = genome

        self.oxygen = 1.0

        self.regulators = {
            "dosR": 0.0,          # Dormancy regulator
            "sigH": 0.0,          # Oxidative stress response
            "sigE": 0.0,          # Cell envelope stress
            "whiB3": 0.0,         # Redox sensing
            "phoP": 0.5,          # Virulence regulation
            "mprA": 0.0
        }              
        
        self.functions = {self.update_functions()}

        self.physiology = {
            "energy": 1.0,
            "metabolism": 1.0,
            "cell_wall": 1.0,
            "redox_balance": 1.0

}

        self.inputs = {
            "oxygen": 1.0,
            "drug": 0.0,
            "immune": 0.0,
            "nutrient": 1.0,
            "redox":0.0,
            "acidic_pH":0.0,
            "nitric_oxide":0.0,
            "iron_limitation":0.0
        }

        self.memory = {

            "dosR": 0.0,
            "sigH": 0.0,
            "sigE": 0.0,
            "mprA": 0.0,
            "phoP": 0.0,
            "whiB3": 0.0

        }

        self.sensitivity = {
            "dosR": genome["dosR_sensitivity"],
            "stress": genome["stress_sensitivity"],
            "growth": genome["growth_sensitivity"]
        }

    def update(self, oxygen, drug=0.0, immune=0.0, nutrient=1.0):

        self.oxygen = oxygen

        self.inputs["oxygen"] = oxygen
        self.inputs["drug"] = drug
        self.inputs["immune"] = immune
        self.inputs["nutrient"] = nutrient

        g = self.regulators

        # Small decay so regulators fade over time
        for gene in g:
            g[gene] *= 0.95

        # ---------- Regulatory interactions ----------

        for _ in range(3):

            new_genes = {}

            for gene in g:

                total_input = (TB_PARAMETERS["memory_current"] * g[gene] + TB_PARAMETERS["memory_previous"] * self.memory.get(gene, 0.0))
    
                total_input += self.environmental_signal(gene)

    # Incoming regulation
                for source, targets in self.genome["grn_weights"].items():

                    if gene in targets:
                        total_input += g[source] * targets[gene]

                new_genes[gene] = self.sigmoid(total_input)

        # Clamp values to [0,1]
            g = new_genes

        self.regulators = new_genes

        self.functions["growth"] = max(
            0.0,
            1.0 - 0.7 * self.regulators["dosR"]
        )

        self.functions["replication"] = self.functions["growth"]

        self.functions["efflux"] = self.regulators["sigE"]

        for gene in self.memory:

            self.memory[gene] = self.regulators[gene]

    def phenotype(self):

        g = self.regulators

        self.current_phenotype = {

            "growth_factor": self.physiology["metabolism"],
            "stress_tolerance": 0.5 * (g["sigH"] + g["sigE"]),
            "dormancy": g["dosR"],
            "virulence": g["phoP"],
            "drug_efflux": self.functions["efflux"] * self.physiology["cell_wall"],
            "persistence": g["mprA"]

        }

        return self.current_phenotype
    
    def state_scores(self):

        p = self.phenotype()

        scores = {

            "ACTIVE":

                (
                    p["growth_factor"]
                    + self.inputs["oxygen"]
                    + self.inputs["nutrient"]
                ) / 3,

            "DORMANT":

                (
                    p["dormancy"]
                    + (1 - self.inputs["oxygen"])
                ) / 2,

            "STRESSED":

                (
                    p["stress_tolerance"]
                    + self.inputs["drug"]
                    + self.inputs["immune"]
                ) / 3,

            "REACTIVATING":

                (
                    p["growth_factor"]
                    + self.inputs["oxygen"]
                    - p["dormancy"]
                ) / 3

        }

        return scores
    
    def choose_state(self):

        scores = self.state_scores()

        return max(

            scores,

            key=scores.get

        )
        
    def sigmoid(self, x):
            return 1.0 / (1.0 + math.exp(-x))
    
    def environmental_signal(self, gene):

        signal = 0.0

        if gene == "dosR":

            signal += (
                (1-self.inputs["oxygen"])
                *TB_PARAMETERS["dosR_activation"]
                *self.sensitivity["dosR"]
            )

        elif gene == "sigH":

            signal += (
                self.inputs["immune"]
                *TB_PARAMETERS["sigH_activation"]
                *self.sensitivity["stress"]
            )

        elif gene == "sigE":

            signal += (
                self.inputs["drug"]
                *TB_PARAMETERS["sigE_activation"]
                *self.sensitivity["stress"]
            )

        elif gene == "whiB3":

            signal += (
                self.inputs["redox"]
                *TB_PARAMETERS["whiB3_activation"]
            )

        return signal
    
    def update_functions(self):

        r = self.regulators
        f = self.functions

        f["growth"] = self.sigmoid(

            TB_PARAMETERS["growth_bias"],
            TB_PARAMETERS["growth_dosR_weight"]*r["dosR"],
            TB_PARAMETERS["growth_sigH_weight"]*r["sigH"],
            TB_PARAMETERS["growth_mprA_weight"]*r["mprA"],
            TB_PARAMETERS["growth_phoP_weight"]*r["phoP"]

        )

        f["replication"] = f["growth"]

        f["efflux"] = self.sigmoid(

            TB_PARAMETERS["efflux_sigE_weight"]*r["sigE"],

            TB_PARAMETERS["efflux_mprA_weight"]*r["mprA"]

        )

    def update_physiology(self):

        r = self.regulators

        f = self.functions

        p = self.physiology

        p["metabolism"] = (
            0.7 * f["growth"]
            + 0.3 * (1 - r["dosR"])
        )

        p["energy"] = (
            0.6 * p["metabolism"]
            + 0.4 * self.inputs["nutrient"]
        )

        p["cell_wall"] = (
            0.7
            + 0.3 * r["sigE"]
        )

        p["redox_balance"] = (
            0.5
            + 0.5 * r["whiB3"]
        )