import random
import copy
import numpy as np


# Gene limits
GENE_BOUNDS = {
    "speed": (0.5, 7.0),
    "vision_radius": (15, 180),
    "energy_efficiency": (0.2, 1.0),
    "size": (3, 14),
    "metabolism": (0.5, 2.0),
}

def random_genome():
    return {
        key: random.uniform(low, high)
        for key, (low, high) in GENE_BOUNDS.items()
    }

def clamp_genome(genome):
    return {
        key: float(np.clip(
            genome[key],
            GENE_BOUNDS[key][0],
            GENE_BOUNDS[key][1]
        ))
        for key in GENE_BOUNDS
    }

def mutate_genome(genome, rate=0.12, strength=0.18):

    child = copy.deepcopy(genome)

    for key, (low, high) in GENE_BOUNDS.items():

        if random.random() < rate:

            mutation = (
                (high - low)
                * strength
                * random.gauss(0, 1)
            )

            child[key] += mutation

    return clamp_genome(child)