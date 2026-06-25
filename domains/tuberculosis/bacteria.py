import random
import math
import uuid
from core.agent import Agent
from domains.tuberculosis.tb_genome import TB_GENE_BOUNDS
from evolution.mutation import gaussian_mutate
from domains.tuberculosis.tb_grn import TBGRN
import copy
from domains.tuberculosis.tb_grn_network import REGULATORY_NETWORK


class Bacteria(Agent):

    ACTIVE = "ACTIVE"

    STRESSED = "STRESSED"

    DORMANT = "DORMANT"

    REACTIVATING = "REACTIVATING"

    DEAD = "DEAD"


    def __init__(self, x, y, genome=None):

        super().__init__()

        self.id = str(uuid.uuid4())[:6]

        self.x = x

        self.y = y

        if genome is None:
         self.genome = {

            "replication_rate": random.uniform(0.002,0.01),

            "inh_resistance": random.uniform(0,0.1),

            "rif_resistance": random.uniform(0,0.1),

            "fluoroquinolone_resistance": random.uniform(0,0.1),

            "injectable_resistance": random.uniform(0,0.1),

            "dormancy_tendency": random.uniform(0,1),

            "virulence": random.uniform(0,1),

            # -------- GRN genes --------

            "dosR_sensitivity": random.uniform(0.8,1.2),

            "stress_sensitivity": random.uniform(0.8,1.2),

            "growth_sensitivity": random.uniform(0.8,1.2),

            "grn_weights": {}

         }

        else:

            self.genome = genome

        for source, targets in REGULATORY_NETWORK.items():

            self.genome["grn_weights"][source] = {}

            for target in targets:

                self.genome["grn_weights"][source][target] = random.uniform(-1.0, 1.0)

        self.state = "ACTIVE"

        self.energy = 50

        self.age = 0

        self.generation = 0

        self.parent_id = None

        self.children = []

        self.mutations = []

        self.birth_tick = 0

        self.lineage_color = (

            random.randint(50,255),

            random.randint(50,255),

            random.randint(50,255)

        )

        self.grn = TBGRN(self.genome)

    def move(self, oxygen_field):

        best_angle = None 
        best_oxygen = -1 
        
        for _ in range(8): 
            angle = random.uniform(0, 2*math.pi) 
            
            test_x = self.x + math.cos(angle) * 10 
            test_y = self.y + math.sin(angle) * 10 
            
            o2 = oxygen_field.oxygen_at( test_x, test_y ) 
            
            if o2 > best_oxygen: 
                best_oxygen = o2 
                best_angle = angle


    def reproduce(self):

        if self.state != Bacteria.ACTIVE:

            return None

        phenotype = self.grn.phenotype()

        probability = (self.genome[ "replication_rate"] * self.grn.current_phenotype["growth_factor"])

        fitness_cost = (

            self.genome["inh_resistance"] * 0.3 +

            self.genome["rif_resistance"] * 0.3 +

            self.genome["fluoroquinolone_resistance"] * 0.2 +

            self.genome["injectable_resistance"] * 0.2

        )

        probability *= (1 - fitness_cost * 0.5)

        if random.random() > probability:

            return None


        child_genome = gaussian_mutate(

            self.genome,
            TB_GENE_BOUNDS

        )

        self.energy -= 20

        if self.energy <= 0:
            self.state = Bacteria.DEAD
            return None

        child = Bacteria(

            self.x + random.randint(-5,5),

            self.y + random.randint(-5,5),

            child_genome

        )


        child.parent_id = self.id

        child.generation = (self.generation + 1)

        child.birth_tick = self.age

        child.lineage_color = (self.lineage_color)

        child.mutations = (self.mutations.copy())

        for gene in self.genome:

            if gene == "grn_weights":
                continue

            old = self.genome[gene]

            new = child.genome[gene]


            if abs(new - old) > 0.05:

                child.mutations.append(
                    {"gene" : gene, 
                      "delta" : round( new-old, 3), 
                      "generation": child.generation
                    }
                )

        return child


    def update(self, oxygen_field):

        self.age += 1

        oxygen = oxygen_field.oxygen_at(self.x, self.y)

        self.grn.update(oxygen)

        g = self.grn.genes

        stress_cost = (
            0.003 * g["sigH"] +
            0.003 * g["sigE"] +
            0.002 * g["mprA"]
        )

        self.energy -= stress_cost

        if random.random() < 0.001:
            print(
                "O2:",
                round(oxygen, 2),
                "dosR:",
                round(self.grn.genes["dosR"], 2),
                "growth:",
                round(self.grn.genes["growth"], 2),
                "stress:",
                round(self.grn.genes["stress"], 2)
            )

        phenotype = self.grn.phenotype()

        if phenotype["dormancy"] > 0.70:

            self.state = Bacteria.DORMANT

        elif phenotype["stress_tolerance"] > 0.50:

            self.state = Bacteria.STRESSED

        else:

            self.state = Bacteria.ACTIVE

        if oxygen > 0.7:

            self.energy += 0.01

        elif oxygen > 0.3:

            self.energy += 0.005

        self.energy = min(self.energy, 100)

        # Oxygen-driven state transition       

        if self.state == Bacteria.DORMANT:

                self.energy -= (0.002 * (1 - self.grn.genes["dosR"]))

                if self.energy <= 0:

                    self.state = Bacteria.DEAD

                return


        self.move(oxygen_field)

        if self.state == Bacteria.ACTIVE:
            loss = 0.01

            loss *= (
                1 - 0.3 * self.grn.genes["mprA"]
            )

            self.energy -= loss

        elif self.state == Bacteria.STRESSED:
            self.energy -= 0.005

        elif self.state == Bacteria.REACTIVATING:
            self.energy -= 0.007

        if self.energy <= 0:
            self.state = Bacteria.DEAD

    @property

    def is_mdr(self):

        return (

        self.genome["inh_resistance"] > 0.7

        and

        self.genome["rif_resistance"] > 0.7

        )
    
    @property

    def is_xdr(self):

        return (

        self.is_mdr

        and

        self.genome["fluoroquinolone_resistance"] > 0.7

        and

        self.genome["injectable_resistance"] > 0.7

        )