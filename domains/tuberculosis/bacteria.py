import random
import math
import uuid
from core.agent import Agent
from domains.tuberculosis.tb_genome import TB_GENE_BOUNDS
from evolution.mutation import gaussian_mutate


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

                random.uniform(0.0002,0.002),

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

    def move(self):

        if self.state != Bacteria.ACTIVE:

            return


        angle = random.uniform(

            0,

            2 * math.pi

        )


        speed = 1
        dx = math.cos(angle)
        dy = math.sin(angle)

        self.x += dx * speed
        self.y += dy * speed


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

        self.energy -= 5

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

        # Oxygen-driven state transition

        if oxygen > 0.7:

            if self.state == Bacteria.DORMANT:

                self.state = Bacteria.REACTIVATING

            elif self.state != Bacteria.REACTIVATING:

                self.state = Bacteria.ACTIVE


        elif oxygen > 0.3:

            self.state = Bacteria.STRESSED


        else:

            self.state = Bacteria.DORMANT     

        if self.state == Bacteria.REACTIVATING:

            if random.random() < 0.03:

                self.state = Bacteria.ACTIVE  

        if self.state == Bacteria.DORMANT:

                self.energy -= 0.002

                if self.energy <= 0:

                    self.state = Bacteria.DEAD

                return


        self.move()

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