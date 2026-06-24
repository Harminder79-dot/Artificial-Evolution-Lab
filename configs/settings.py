# ── World ──────────────────────────────────────────────────────────────────────
WORLD_WIDTH          = 1100
WORLD_HEIGHT         = 800
FPS                  = 30
BG_COLOR             = (12, 12, 22)

# ── Population ─────────────────────────────────────────────────────────────────
INITIAL_ORGANISMS    = 30
MAX_ORGANISMS        = 80
INITIAL_FOOD         = 40
MAX_AGE              = 3000

# ── Food ───────────────────────────────────────────────────────────────────────
FOOD_SPAWN_RATE      = 0.7
FOOD_ENERGY          = 45
FOOD_RADIUS          = 4
FOOD_COLOR           = (60, 200, 90)

# ── Energy ─────────────────────────────────────────────────────────────────────
STARTING_ENERGY      = 100.0
MOVE_ENERGY_BASE     = 0.015
IDLE_ENERGY_BASE     = 0.01
REPRODUCTION_COST    = 25.0
REPRODUCTION_THRESH  = 70.0

# ── Evolution ──────────────────────────────────────────────────────────────────
MUTATION_RATE        = 0.7
MUTATION_STRENGTH    = 0.36
CROSSOVER_RATE       = 0.5
ELITISM_COUNT        = 5

#── Quantum Mutation ──────────────────────────────────────────────────────────────────
QUANTUM_ENTROPY = 0.4
USE_QUANTUM_MUTATION = True

# ── Predators ──────────────────────────────────────────────

INITIAL_PREDATORS = 5

PREDATOR_SPEED = 3.8
PREDATOR_VISION = 140

PREDATOR_STARTING_ENERGY = 150
PREDATOR_KILL_ENERGY = 80

PREDATOR_REPRODUCTION_THRESH = 250
PREDATOR_REPRODUCTION_COST = 100

MAX_PREDATORS = 10

PREDATOR_MAX_AGE = 2500

PREDATOR_ATTACK_RADIUS = 10