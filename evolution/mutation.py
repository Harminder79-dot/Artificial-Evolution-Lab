import numpy as np
import random
import copy

from agents.genome import GENE_BOUNDS, clamp_genome
from configs.settings import QUANTUM_ENTROPY


# ── Classical Gaussian Mutation ──────────────────────────────────────────────

def gaussian_mutate(genome: dict, gene_bounds: dict, rate: float = 0.12, strength: float = 0.40) -> dict:

    child = copy.deepcopy(genome)

    for key, (lo, hi) in gene_bounds.items():

        if random.random() < rate:

            child[key] += (
                (hi - lo)
                * strength
                * random.gauss(0, 1)
            )

    for key,(lo,hi) in gene_bounds.items():

        child[key] = max(lo, min(hi, child[key]))

    if "grn_weights" in child:

        EDGE_MUTATION_RATE = 0.05
        EDGE_SIGMA = 0.05

        for source, targets in child["grn_weights"].items():

            for target in targets:

                if random.random() < EDGE_MUTATION_RATE:

                    targets[target] += random.gauss(
                        0,
                        EDGE_SIGMA
                    )

                    targets[target] = max(
                        -1.0,
                        min(
                            1.0,
                            targets[target]
                        )
                    )

# ── Quantum-Inspired Mutation ────────────────────────────────────────────────

_STRATEGIES = [
    "small_nudge",
    "large_jump",
    "directional_improve",
    "no_change"
]


def _softmax(x: np.ndarray) -> np.ndarray:

    e = np.exp(x - np.max(x))

    return e / e.sum()


def quantum_mutate(genome: dict, entropy: float = QUANTUM_ENTROPY) -> dict:

    child = copy.deepcopy(genome)

    for key, (lo, hi) in GENE_BOUNDS.items():

        base_weights = np.array([
            1.0 - entropy * 0.3,
            entropy * 0.8,
            0.6,
            (1.0 - entropy) * 0.5,
        ])

        probs = _softmax(base_weights)

        strategy = np.random.choice(_STRATEGIES, p=probs)

        span = hi - lo

        if strategy == "small_nudge":

            child[key] += (
                span
                * 0.05
                * random.gauss(0, 1)
            )

        elif strategy == "large_jump":

            child[key] = random.uniform(lo, hi)

        elif strategy == "directional_improve":

            sign = (
                +1
                if key in ("energy_efficiency", "vision_radius")
                else random.choice([-1, 1])
            )

            child[key] += (
                sign
                * span
                * 0.08
                * abs(random.gauss(0, 1))
            )

    return clamp_genome(child)


# ── Adaptive Mutation Rate ───────────────────────────────────────────────────

def adaptive_mutation_rate(population_diversity: float) -> float:

    base_rate = 0.12

    if population_diversity < 0.15:
        return min(base_rate * 2.5, 0.45)

    if population_diversity > 0.5:
        return max(base_rate * 0.5, 0.04)

    return base_rate