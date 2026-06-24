import random
import math
import uuid
from core.agent import Agent
from domains.tuberculosis.tb_genome import TB_GENE_BOUNDS
from evolution.mutation import gaussian_mutate
from domains.tuberculosis.tb_grn import TBGRN


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

        self.genome = genome or {

            "replication_rate":

                random.uniform(0.002,0.01),

            "inh_resistance":

                random.uniform(0,0.1),

            "rif_resistance":

                random.uniform(0,0.1),

            "fluoroquinolone_resistance":

                random.uniform(0,0.1),

            "injectable_resistance":

                random.uniform(0,0.1),

            "dormancy_tendency":

                random.uniform(0,1),

            "virulence":

                random.uniform(0,1)

        }

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

        self.grn = TBGRN()

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

        probability = self.genome[ "replication_rate"]

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

        self.state = self.grn.dominant_state()

        if oxygen > 0.7:

            self.energy += 0.01

        elif oxygen > 0.3:

            self.energy += 0.005

        self.energy = min(self.energy, 100)

        # Oxygen-driven state transition       

        if self.state == Bacteria.DORMANT:

                self.energy -= 0.002

                if self.energy <= 0:

                    self.state = Bacteria.DEAD

                return


        self.move(oxygen_field)

        if self.state == Bacteria.ACTIVE:
            self.energy -= 0.01

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