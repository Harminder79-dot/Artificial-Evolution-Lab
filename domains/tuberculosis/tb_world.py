import random
import csv
import os
import math
import pygame
from domains.tuberculosis.granuloma import Granuloma
from domains.tuberculosis.immune_cell import ImmuneCell
from domains.tuberculosis.oxygen_field import OxygenField
from domains.tuberculosis.tb_observables import TBObservables
from domains.tuberculosis.tb_metabolism import TBMetabolism
from domains.tuberculosis.tb_analytics import TBAnalytics
from domains.tuberculosis.cytokine_field import CytokineField
from domains.tuberculosis.camera import Camera
from configs.settings import (

    WORLD_WIDTH,

    WORLD_HEIGHT,

    FPS

)
from domains.tuberculosis.macrophage import Macrophage
from domains.tuberculosis.bacteria import Bacteria
from domains.tuberculosis.tb_renderer import TBRenderer
from domains.tuberculosis.tb_validator import TBValidator
from domains.tuberculosis.tb_calibration import TBCalibration
import time

class TBWorld:

    def __init__(self, config, manager):

        super().__init__()

        self.config = config

        self.manager = manager

        self.tick = 0

        self.total_births = 0

        self.total_deaths = 0

        self.first_dormancy_tick = None

        os.makedirs("experiments", exist_ok=True)

        self.experiment_name = self.config["experiment"]["name"]

        self.csv_file = open(

            self.manager.path(

                "transition_log.csv"

            ),

            "w",

            newline=""

        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([

            "Tick",

            "Population",

            "Active%",

            "Dormant%",

            "Stress%",

            "AverageFitness",

            "AverageATP",

            "AverageGrowth",

            "AverageDosR",

            "Generation",

            "LivingLineages"

        ])

        self.start_time = time.time()

        self.peak_population = 0

        self.lowest_population = float("inf")

        self.metabolism = TBMetabolism()

        self.treatment = {

            "INH": self.config["treatment"]["INH"],

            "RIF": self.config["treatment"]["RIF"],

            "PZA": self.config["treatment"]["PZA"],

            "EMB": self.config["treatment"]["EMB"]

        }

        self.experiment = self.config["experiment"]["name"]

        self.analytics = TBAnalytics()

        self.validator = TBValidator()

        self.observables = TBObservables()

        self.cytokines = CytokineField(
            WORLD_WIDTH, 
            WORLD_HEIGHT,
            decay_rate=self.config["environment"]["cytokine_decay"]
        )

        self.camera = Camera()

        self.dragging = False

        self.last_mouse = (0, 0)

        self.bacteria = []

        self.lineages = {}

        self.lineage_stats = {}

        self.bacteria_by_id = {}

        self.granulomas = []

        self.granulomas.append(
            Granuloma(
                WORLD_WIDTH//2,
                WORLD_HEIGHT//2,
                80
            )
        )

        self.avg_inh_history = []

        self.avg_rif_history = []

        self.population_history = []

        self.grn_history = {

            "dosR": [],

            "sigH": [],

            "sigE": [],

            "phoP": [],

            "mprA": [],

            "whiB3": []

        }

        self.mdr_history = []

        self.renderer = TBRenderer()

        self.selected_bacteria = None

        self.oxygen = OxygenField(
            WORLD_WIDTH, 
            WORLD_HEIGHT,
            diffusion_rate=self.config["environment"]["oxygen_diffusion"],
            decay_rate=self.config["environment"]["oxygen_decay"]
        )

        self.paused = False

        self.simulation_speed = self.config["simulation"]["speed"]

        self.debug = True

        self.debug_stats = {}

    # Simulation history (last 500 ticks)

        self.history = {

            "population": [],
            "energy": [],
            "growth": [],
            "stress": [],
            "dormancy": [],
            "dosR": [],
            "virulence": [],
            "replication": [],
            "cytokine": [],
            "oxygen": []

        }

        self.immune_cells = []

        for _ in range(self.config["population"]["initial_immune"]):

            cell = ImmuneCell(

                random.randint(0,WORLD_WIDTH),

                random.randint(0,WORLD_HEIGHT)

            )

            self.immune_cells.append(cell)

        for _ in range(self.config["population"]["initial_bacteria"]):


            b = Bacteria(

                WORLD_WIDTH//2 + random.randint(-40,40),

                WORLD_HEIGHT//2 + random.randint(-40,40),

                config=self.config

            )

    

            self.lineage_stats[b.id] = {
                "founder": b.id,
                "birth_tick": 0
            }

            self.bacteria.append(b)

            self.lineages[b.id] = {

                "parent": None,

                "children": []

            }

            self.lineage_stats[b.id] = {
                "founder": b.id,
                "birth_tick": self.tick
            }

        self.macrophages = []


        for _ in range(self.config["population"]["initial_macrophages"]):

            self.macrophages.append(

                Macrophage(

                    random.randint(

                        0,

                        WORLD_WIDTH

                    ),

                    random.randint(

                        0,

                        WORLD_HEIGHT

                    )

                )
            )

    def update(self):

        self.tick += 1

        self.update_environment()

        new_granuloma_bacteria = self.update_granulomas()

        self.bacteria.extend(new_granuloma_bacteria)

        granuloma_added = len(new_granuloma_bacteria)

        reproduction_added = 0

        macrophage_added = 0

        if granuloma_added:

            print(
                f"Granuloma added "
                f"{len(new_granuloma_bacteria)} bacteria"
            )

        # Macrophage <-> TB interactiprinton

        for m in self.macrophages:

            for b in self.bacteria[:]:

                if b.state == Bacteria.DEAD:

                    continue

                if m.state != Macrophage.HEALTHY:

                    continue

                dx = b.x - m.x

                dy = b.y - m.y

                if dx*dx + dy*dy < 64:   
                    
                    kill_prob = max(
                        0.35, 
                        0.9 - m.exhaustion
                    )

                    if random.random() < kill_prob:

                        b.state = Bacteria.DEAD


                    else:

                        m.infect()

                        b.state = Bacteria.DEAD

                        print("MACROPHAGE INFECTED")

                        print(
                            f"INFECTED MACROPHAGE "
                            f"TB:{b.id}"
                        )

                    break

        #if self.tick == 2000:
#
 #           self.treatment["INH"] = True
  #          self.treatment["RIF"] = True
   #         self.treatment["PZA"] = True
    #        self.treatment["EMB"] = True


     #   if self.tick == 5000:

#            self.treatment["INH"] = False
 #           self.treatment["RIF"] = False
  #          self.treatment["PZA"] = False
   #         self.treatment["EMB"] = False

        newborns = []
        births = 0

        for b in self.bacteria[:]:

            b.update(self.oxygen)

            if (
                self.first_dormancy_tick is None
                and
                b.state == Bacteria.DORMANT
            ):

                self.first_dormancy_tick = self.tick

            self.apply_treatment(b)

            if b.state == Bacteria.DEAD:

                continue

            child = b.reproduce(self)


            if child:
                
                births += 1
                reproduction_added += 1
                self.total_births += 1
                newborns.append(child)

                self.lineages[child.id] = {

                    "parent": b.id,

                    "children": []

                }

                founder = self.lineage_stats[b.id]["founder"]

                self.lineage_stats[child.id] = {
                    "founder": founder,
                    "birth_tick": self.tick
                }


                self.lineages[b.id]["children"].append(

                    child.id

                )


        self.bacteria.extend(newborns)

        if self.tick % 10 == 0:

            self.bacteria_by_id = {

                b.id : b

                for b in self.bacteria

            }

        new_bacteria = []

        for m in self.macrophages:

            if m.state == Macrophage.INFECTED:

                self.cytokines.deposit(m.x, m.y, amount=0.6)

            burst = m.update(self.bacteria)

            if burst:

                print(

                    f"Macrophage burst -> "

                    f"{m.intracellular_tb} TB released"

                )

                for _ in range(m.intracellular_tb):               

                    angle = random.uniform(0, 2*math.pi)

                    radius = random.uniform(5,40)

                    child = Bacteria(

                        m.x + radius*math.cos(angle),

                        m.y + radius*math.sin(angle), 

                        config=self.config
                    )

                    self.lineages[child.id] = {
                        "parent": None,
                        "children": []
                    }

                    self.lineage_stats[child.id] = {
                        "founder": child.id,
                        "birth_tick": self.tick
                    }

                    new_bacteria.append(child)

        # Recruit new macrophages based on inflammation
        if self.tick % 300 == 0:

            if (
                self.cytokines.grid.max() > 2
                and len(self.macrophages) < 150
            ):

                self.macrophages.append(

                    Macrophage(

                        random.randint(0, WORLD_WIDTH),
                        random.randint(0, WORLD_HEIGHT)

                    )

                )

                print("New macrophage recruited")

        MAX_BACTERIA = 2000

        if len(self.bacteria) < MAX_BACTERIA:
            self.bacteria.extend(new_bacteria)

        macrophage_added = len(new_bacteria)

        if len(new_bacteria) > 0:

            print(
                f"Macrophages added "
                f"{len(new_bacteria)} bacteria"
            )

        alive = []

        for b in self.bacteria:

            if b.state == Bacteria.DEAD:

                self.total_deaths += 1

            else:

                alive.append(b)

        self.bacteria = alive

        self.macrophages = [

            m

            for m in self.macrophages

            if m.state != Macrophage.DEAD

        ]

        if self.tick % 100 == 0:

            self.report_cytokines()
            self.report_oxygen()
            self.report_grn()
            self.report_observables()
            self.report_phenotype()
            self.report_validation()
            self.report_evolution()
            self.report_fitness()
            self.report_state_scores()

            active = sum(
                1 for b in self.bacteria
                if b.state == Bacteria.ACTIVE
            )

            dormant = sum(
                1 for b in self.bacteria
                if b.state == Bacteria.DORMANT
            )

            stressed = sum(
                1 for b in self.bacteria
                if b.state == Bacteria.STRESSED
            )

            print(
                f"ACTIVE:{active} "
                f"DORMANT:{dormant} "
                f"STRESSED:{stressed}"
            )

            inside = 0

            for b in self.bacteria:    
                
                d = math.hypot(
                    b.x - self.granulomas[0].x,
                    b.y - self.granulomas[0].y
                )

                if d < self.granulomas[0].radius:
                    inside += 1

            if self.bacteria:

                for regulator in self.grn_history:

                    avg = sum(

                        b.grn.regulators[regulator]

                        for b in self.bacteria

                    ) / len(self.bacteria)

                    self.grn_history[regulator].append(avg)

            for gene in [

                "dosR",
                "sigH",
                "sigE",
                "mprA",
                "phoP",
                "whiB3"

            ]:

                if self.debug_stats[f"{gene}_std"] < 0.02:

                    print(

                        f"[WARNING] {gene} appears frozen."

                    )

            self.csv_writer.writerow([

                self.tick,

                self.debug_stats["population"],

                self.debug_stats["active_percent"],

                self.debug_stats["dormant_percent"],

                self.debug_stats["stressed_percent"],

                self.debug_stats["average_fitness"],

                self.validator.latest(self.observables.history, 'average_atp'),

                self.validator.latest(self.observables.history, 'average_growth'),

                self.validator.latest(self.observables.history,'average_dosR'),

                self.debug_stats["max_generation"],

                self.debug_stats["living_lineages"]

            ])

            self.csv_file.flush()

            self.analytics.record(self)

            if self.debug_stats["population"] > 5000:
                print("[WARNING] Population explosion.")

            if self.debug_stats["population"] == 0:
                print("[WARNING] Population extinct.")

            elif self.debug_stats["population"] < 10:
                print("[WARNING] Population critically low.")

        if self.tick % 200 == 0:

            for m in self.macrophages:

                if m.state != Macrophage.INFECTED:

                    continue


                nearby_immune = 0


                for immune in self.immune_cells:

                    d = math.hypot(

                        immune.x - m.x,

                        immune.y - m.y

                    )


                    if d < 60:

                        nearby_immune += 1


                if nearby_immune > 15:

                    already_exists = False


                    for g in self.granulomas:

                        d = math.hypot(

                            m.x - g.x,

                            m.y - g.y

                        )


                        if d < g.radius:

                            already_exists = True

                            break


                    if not already_exists:

                        self.granulomas.append(

                            Granuloma(

                                m.x,

                                m.y,

                                50

                            )

                        )

        for immune in self.immune_cells:

            immune.move_up_cytokine_gradient(self.cytokines)

            strongest = None

            signal = 0


            #for m in self.macrophages:

            #    if m.signal_strength > signal:

            #        signal = m.signal_strength

            #        strongest = m


            if strongest:

                immune.move_towards(

                    strongest.x,

                    strongest.y

                )

                if signal > 0.7:

                    if random.random() < 0.003:

                        self.macrophages.append(

                            Macrophage(

                                strongest.x + random.randint(-40,40),

                                strongest.y + random.randint(-40,40)

                            )

                        )

        self.camera.update()

        self.compute_debug_stats()

    def report_cytokines(self):
        print(

            "Max Cytokine:",

            round(self.cytokines.grid.max(), 3)

        )

        print(

            f"Cytokine Avg : "

            f"{self.debug_stats['cytokine_average']:.3f}"

        )

        print(

            f"Cytokine Std : "

            f"{self.debug_stats['cytokine_std']:.3f}"

        )

        print(

            f"Hotspots : "

            f"{self.debug_stats['cytokine_hotspots']}"

        )

        print(

            f"Infected Macrophages : "

            f"{self.debug_stats['infected_macrophages']}"

        )

        if self.debug_stats["infected_macrophages"] > 0:

            print(
                "Recruitment Ratio:",
                round(
                    len(self.macrophages)
                    /
                    self.debug_stats["infected_macrophages"],
                    2
                )
            )


    def report_oxygen(self):
        print(
                "Oxygen:",
                self.oxygen.grid.min(),
                self.oxygen.grid.max(),
                min(self.oxygen.grid.flatten()),
                max(self.oxygen.grid.flatten())
            )

        print(

            f"O2 Avg : "

            f"{self.debug_stats['oxygen_average']:.3f}"

        )

        print(

            f"O2 Std : "

            f"{self.debug_stats['oxygen_std']:.3f}"

        )

        print(

            f"Hypoxic TB : "

            f"{self.debug_stats['hypoxic_bacteria']}"

        )

    def report_grn(self):
        print("\nAverage GRN Activity")

        low_o2 = []

        high_o2 = []

        for b in self.bacteria:

            o2 = self.oxygen.oxygen_at(
                b.x,
                b.y
            )

            if o2 < 0.30:

                low_o2.append(
                    b.grn.regulators["dosR"]
                )

            else:

                high_o2.append(
                    b.grn.regulators["dosR"]
                )

        for regulator in self.grn_history:

            if self.grn_history[regulator]:

                print(

                    regulator,

                    round(

                        self.grn_history[regulator][-1],

                        3

                    )

                )

        print("\n========== GRN RESPONSE ==========")

        for gene in [

            "dosR",
            "sigH",
            "sigE",
            "mprA",
            "phoP",
            "whiB3"

        ]:

            values = [

                b.grn.regulators[gene]

                for b in self.bacteria

                if b.state != Bacteria.DEAD

            ]

            if values:

                print(

                    f"{gene:7s}",

                    "Mean =",

                    round(

                        sum(values) / len(values),

                        3

                    ),

                    "| Std =",

                    round(

                        self.debug_stats[f"{gene}_std"],

                        3

                    )

                )

        print("==================================")


    def report_observables(self):
        self.observables.record(self)

        print(
            f"Population: {self.observables.history['population'][-1]}"
        )

        print(
            f"DosR: {self.validator.latest(self.observables.history, 'average_dosR'):.3f}"
        )

        print(
            f"ATP: {self.validator.latest(self.observables.history, 'average_atp'):.3f}"
        )

        print(
            f"Redox: {self.validator.latest(self.observables.history, 'average_redox'):.3f}"
        )

        history = self.observables.history["average_grn_weight"]

        if history:
            print(f"Avg GRN Weight: {history[-1]:.3f}")
        else:
            print("Avg GRN Weight: N/A")


        print(
            f"Health: {self.validator.latest(self.observables.history, 'average_cell_health'):.3f}")

    def report_phenotype(self):
        print("\n========== PHENOTYPE REPORT ==========")

        print(

            f"ACTIVE: "

            f"{self.debug_stats['active_percent']:.1f}%"

        )

        print(

            f"STRESSED: "

            f"{self.debug_stats['stressed_percent']:.1f}%"

        )

        print(

            f"DORMANT: "

            f"{self.debug_stats['dormant_percent']:.1f}%"

        )

        print(

            f"REACTIVATING: "

            f"{self.debug_stats['reactivating_percent']:.1f}%"

        )

        print("======================================")

    def report_validation(self):
        if self.debug_stats["active_percent"] > 95:

            print(

                "[WARNING] Population almost entirely ACTIVE."

            )

        if self.debug_stats["dormant_percent"] > 90:

            print(

                "[WARNING] Population almost entirely DORMANT."

            )

    def report_evolution(self):
        print("\n========== EVOLUTION REPORT ==========")

        print(
            f"Population          : {self.debug_stats['population']}"
        )

        print(
            f"Living Lineages     : {self.debug_stats['living_lineages']}"
        )

        print(
            f"Max Generation      : {self.debug_stats['max_generation']}"
        )

        print(
            f"Average Generation  : "
            f"{self.debug_stats['average_generation']:.2f}"
        )

        print(
            f"Largest Family      : {self.debug_stats['largest_family']}"
        )

        print(
            f"Unique Genomes      : {self.debug_stats['unique_genomes']}"
        )

        print(
            f"Average Mutations   : "
            f"{self.debug_stats['average_mutations']:.2f}"
        )

        print("======================================\n")


    def report_fitness(self):

        print("\n========== FITNESS REPORT ==========")

        print(
            
            "Average Fitness:",

            round(

                self.debug_stats["average_fitness"],
                2
            )
        )

        print(

            "Best Fitness:",

            round(

                self.debug_stats["best_fitness"],
                2
            )
        )

        print(

            "Average Fitness:",

            round(

                self.debug_stats["average_fitness"],
                2
            )
        )

        print(

            "Best Generation:",
            self.debug_stats["best_generation"]

        )

        print(

            "Best Bacterium:",
            self.debug_stats["best_id"]

        )

        print("====================================")

    def report_state_scores(self):

        print("\n========== STATE SCORE CHECK ==========")

        sample = None

        for b in self.bacteria:

            if b.state != Bacteria.DEAD:

                sample = b

                break

        if sample:

            for state, value in sample.grn.last_scores.items():

                print(

                    f"{state:12s}: {value:.3f}"

                )

        print("======================================")

    def compute_debug_stats(self):

        alive = [b for b in self.bacteria if b.state != Bacteria.DEAD]

        best = max(
            alive,
            key=lambda b: b.fitness,
            default=None
        )

        active = 0

        stressed = 0

        dormant = 0

        reactivating = 0

        for b in alive:

            if b.state == Bacteria.ACTIVE:

                active += 1

            elif b.state == Bacteria.STRESSED:

                stressed += 1

            elif b.state == Bacteria.DORMANT:

                dormant += 1

            elif b.state == Bacteria.REACTIVATING:

                reactivating += 1

        gene_std = {}

        for gene in [
            "dosR",
            "sigH",
            "sigE",
            "mprA", 
            "phoP",
            "whiB3"
        ]:

            values = [

                b.grn.regulators[gene]

                for b in alive

            ]

            if values:

                mean = sum(values)/len(values)

                variance = sum(

                    (v-mean)**2

                    for v in values

                )/len(values)

                gene_std[gene] = math.sqrt(variance)

            else:

                gene_std[gene] = 0

        infected_macrophages = sum(

            1

            for m in self.macrophages

            if m.state == Macrophage.INFECTED

        )

        hypoxic = 0

        for b in alive:

            o2 = self.oxygen.oxygen_at(b.x, b.y)

            if o2 < 0.30:

                hypoxic += 1

        if not self.bacteria:
            return

        N = max(1, len(alive))

        self.peak_population = max(

            self.peak_population,

            len(alive)

        )

        self.lowest_population = min(

            self.lowest_population,

            len(alive)

        )

        self.debug_stats = {

            "population": len(alive),

            "peak_population":
                self.peak_population,

            "lowest_population":
                self.lowest_population,

            "runtime":
                time.time() - self.start_time,

            "average_fitness": sum(
                b.fitness
                for b in alive
            ) / N,

            "best_fitness":max(
                b.fitness
                for b in alive
            ),

            "best_generation":
                best.generation
                if best
                else 0,

            "best_id":
                best.id
                if best
                else "None",

            "active_percent":
                100 * active / N,

            "stressed_percent":
                100 * stressed / N,

            "dormant_percent":
                100 * dormant / N,

            "reactivating_percent":
                100 * reactivating / N,

            "hypoxic_bacteria": hypoxic,

            "births": 0,

            "deaths": 0,

            "avg_energy":
                sum(b.energy for b in alive) / N,

            "avg_growth":
                sum(
                    b.grn.current_phenotype.get("growth_factor", 0.0)
                    for b in alive
                ) / N,

            "avg_dormancy":
                sum(
                    b.grn.current_phenotype.get("dormancy", 0.0)
                    for b in alive
                ) / N,

            "avg_stress":
                sum(
                    b.grn.current_phenotype.get("stress_tolerance", 0.0)
                    for b in alive
                ) / N,

            "avg_dosR":
                sum(
                    b.grn.regulators["dosR"]
                    for b in alive
                ) / N,

            "avg_sigH":
                sum(
                    b.grn.regulators["sigH"]
                    for b in alive
                ) / N,

            "avg_sigE":
                sum(
                    b.grn.regulators["sigE"]
                    for b in alive
                ) / N,

            "dosR_std":
                gene_std["dosR"],

            "sigH_std":
                gene_std["sigH"],

            "sigE_std":
                gene_std["sigE"],

            "mprA_std":
                gene_std["mprA"],

            "phoP_std":
                gene_std["phoP"],

            "whiB3_std":
                gene_std["whiB3"],

            "avg_mprA":
                sum(
                    b.grn.regulators["mprA"]
                    for b in alive
                ) / N,

            "avg_replication":
                sum(
                    b.genome["replication_rate"]
                    for b in alive
                ) / N,

            "avg_virulence":
                sum(
                    b.genome["virulence"]
                    for b in alive
                ) / N,

            "avg_dormancy_gene":
                sum(
                    b.genome["dormancy_tendency"]
                    for b in alive
                ) / N,

            "oxygen_min":
                float(self.oxygen.grid.min()),

            "oxygen_max":
                float(self.oxygen.grid.max()),

            "oxygen_average":
                float(self.oxygen.grid.mean()),

            "oxygen_std":
                float(self.oxygen.grid.std()),

            "cytokine_max":
                float(self.cytokines.grid.max()),

            "cytokine_average":
                float(self.cytokines.grid.mean()),

            "cytokine_std":
                float(self.cytokines.grid.std()),

            "infected_macrophages":
                infected_macrophages,

            "macrophages":
                len(self.macrophages),

            "granulomas":
                len(self.granulomas),

            "max_generation":
                max(
                    b.generation
                    for b in alive
                ) if alive else 0,

            "average_generation":
                sum(
                    b.generation
                    for b in alive
                ) / N,

            "unique_genomes":
                len({

                    (
                        round(b.genome["replication_rate"],3),
                        round(b.genome["virulence"],3),
                        round(b.genome["dormancy_tendency"],3)

                    )

                    for b in alive

                }),

            "average_mutations":
                sum(
                    len(b.mutations)
                    for b in alive
                ) / N,

            "oldest_age":
                max(
                    b.age
                    for b in alive
                ) if alive else 0,

            "largest_family":
                max(
                    len(b.children)
                    for b in alive
                ) if alive else 0,

            "living_lineages":
                len({
                    self.lineage_stats[b.id]["founder"]
                    for b in alive
                }),
        }

            # Store history

        self.history["population"].append(len(self.bacteria))

        self.history["energy"].append(
            self.debug_stats["avg_energy"]
        )

        self.history["growth"].append(
            self.debug_stats["avg_growth"]
        )

        self.history["stress"].append(
            self.debug_stats["avg_stress"]
        )

        self.history["dormancy"].append(
            self.debug_stats["avg_dormancy"]
        )

        self.history["dosR"].append(
            self.debug_stats["avg_dosR"]
        )

        self.history["virulence"].append(
            self.debug_stats["avg_virulence"]
        )

        self.history["replication"].append(
            self.debug_stats["avg_replication"]
        )

        self.history["cytokine"].append(
            self.debug_stats["cytokine_max"]
        )

        self.history["oxygen"].append(
            self.debug_stats["oxygen_min"]
        )

        hotspots = 0

        for row in range(self.cytokines.rows):

            for col in range(self.cytokines.cols):

                if self.cytokines.grid[row, col] > 2.0:

                    hotspots += 1

        self.debug_stats["cytokine_hotspots"] = hotspots

        MAX_HISTORY = 500

        for values in self.history.values():

            if len(values) > MAX_HISTORY:

                values.pop(0)

    def update_environment(self):

        self.oxygen.consume_oxygen(self.bacteria)

        self.cytokines.update()

    def run(self):

        clock = pygame.time.Clock()

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_o:
                        self.renderer.show_oxygen = not self.renderer.show_oxygen

                    elif event.key == pygame.K_c:
                        self.renderer.show_cytokines = not self.renderer.show_cytokines

                    elif event.key == pygame.K_F1:
                        self.debug = not self.debug

                    elif event.key == pygame.K_r:
                        self.camera.reset()

                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    elif event.key == pygame.K_PERIOD:
                        self.simulation_speed = min(16, self.simulation_speed * 2)

                    elif event.key == pygame.K_COMMA:
                        self.simulation_speed = max(1, self.simulation_speed // 2)

                    elif event.key == pygame.K_n:
                        if self.paused:
                            for _ in range(self.simulation_speed):
                                self.update()

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    # Right click → start dragging
                    if event.button == 3:
                        self.dragging = True
                        self.last_mouse = pygame.mouse.get_pos()

                    # Left click → select bacteria
                    elif event.button == 1:

                        mx, my = pygame.mouse.get_pos()
                        mx, my = self.camera.screen_to_world(mx, my)

                        self.selected_bacteria = None

                        for b in self.bacteria:
                            if math.hypot(b.x - mx, b.y - my) < 8:
                                self.selected_bacteria = b
                                break

                elif event.type == pygame.MOUSEBUTTONUP:

                    if event.button == 3:
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:

                    if self.dragging:

                        mx, my = pygame.mouse.get_pos()

                        dx = mx - self.last_mouse[0]
                        dy = my - self.last_mouse[1]

                        self.camera.move(
                            -dx / self.camera.zoom,
                            -dy / self.camera.zoom
                        )

                        self.last_mouse = (mx, my)

                elif event.type == pygame.MOUSEWHEEL:

                    if event.y > 0:
                        self.camera.zoom_in()

                    elif event.y < 0:
                        self.camera.zoom_out()

            keys = pygame.key.get_pressed()

            speed = 15

            if keys[pygame.K_w]:
                self.camera.move(0, -speed)

            if keys[pygame.K_s]:
                self.camera.move(0, speed)

            if keys[pygame.K_a]:
                self.camera.move(-speed, 0)

            if keys[pygame.K_d]:
                self.camera.move(speed, 0)

            if not self.paused:

                for _ in range(self.simulation_speed):

                    self.update()

            history_size = len(self.history["population"])

            self.renderer.draw(

                self.bacteria,
                self.granulomas,
                self.tick,
                self.immune_cells,
                self.treatment,
                self.oxygen,
                self.cytokines,
                self.macrophages,
                self.selected_bacteria,
                self.bacteria_by_id,
                self.camera,
                self.paused,
                self.simulation_speed,
                self.debug_stats,
                history_size
            )

            pygame.display.flip()

            clock.tick(
                self.config["simulation"]["fps"]
            )

        self.validate()

        self.csv_file.close()

        pygame.quit()
        return

    def update_oxygen(self):

        self.oxygen.grid[:] = 1.0

        for g in self.granulomas:

            for row in range(self.oxygen.rows):

                for col in range(self.oxygen.cols):

                    x = col * self.oxygen.resolution

                    y = row * self.oxygen.resolution

                    d = math.hypot(

                        x - g.x,

                        y - g.y

                    )

                    if d < g.radius:

                        factor = d / g.radius

                        oxygen = 0.1 + 0.9 * factor

                        self.oxygen.grid[row,col] = min(

                            self.oxygen.grid[row,col],

                            oxygen

                        )

    def print_ancestry(self, bacterium):

            current = bacterium.id

            lineage = []


            while current is not None:

                lineage.append(current)

                current = self.lineages[current]["parent"]


            lineage.reverse()

            print(

                " -> ".join(lineage)

            )

    def apply_treatment(self, b):

        if self.treatment["INH"]:

            efflux = b.grn.functions["efflux"]

            effective_resistance = min(
                1.0,
                b.genome["inh_resistance"] + 0.3 * efflux
            )

            prob = 0.002 * (1 - effective_resistance)

            if (

                b.state == Bacteria.ACTIVE

                and

                random.random() < prob

            ):

                b.state = Bacteria.DEAD


        if self.treatment["RIF"]:

            prob = 0.0015 * (

                1 -

                b.genome["rif_resistance"]

            )

            if (

                b.state in [

                    Bacteria.ACTIVE,

                    Bacteria.STRESSED

                ]

                and

                random.random() < prob

            ):

                b.state = Bacteria.DEAD

    def update_granulomas(self):

        new_granuloma_bacteria = []

        if self.tick % 20 == 0:
          

            for g in self.granulomas:

                dormant_tb = 0

                for b in self.bacteria:

                    if b.state != Bacteria.DORMANT:

                        continue

                    d = math.hypot(

                        b.x - g.x,

                        b.y - g.y

                    )

                    if d < g.radius:

                        dormant_tb += 1

            burst = g.update(dormant_tb)

            if burst:

                for _ in range(20):

                    b = Bacteria(

                        g.x +

                        random.randint(-40,40),

                        g.y +

                        random.randint(-40,40),
                        
                        config=self.config

                    )

                    b.state = Bacteria.ACTIVE

                    new_granuloma_bacteria.append(b)

                    self.lineages[b.id] = {

                        "parent": None,

                        "children": []

                    }

                    self.lineage_stats[b.id] = {
                        "founder": b.id,
                        "birth_tick": self.tick
                    }

        return new_granuloma_bacteria
    
    def bacteria_near(self, x, y, radius):

        count = 0

        r2 = radius * radius

        for b in self.bacteria:

            if b.state == Bacteria.DEAD:
                continue

            dx = b.x - x
            dy = b.y - y

            if dx*dx + dy*dy < r2:
                count += 1

        return count
    
    def validate(self):

        if not self.debug_stats:
            return

        self.validator.check(

            self.debug_stats["active_percent"] > 40,

            "Population remained active.",

            "Population activity too low."

        )

        self.validator.check(

            self.debug_stats["population"] > 0,

            "Population survived.",

            "Population went extinct."

        )

        self.validator.check(

            self.debug_stats["dormant_percent"] < 80,

            "Dormancy within expected range.",

            "Dormancy extremely high."

        )
        
        self.validator.check(

            self.debug_stats["average_fitness"] > 0.25,

            "Population fitness healthy.",

            "Population fitness collapsed."

        )

        self.validator.check(

            self.validator.latest(self.observables.history,'average_atp') > 0.30,

            "ATP production maintained.",

            "ATP critically low."

        )

        self.validator.check(

            self.debug_stats["avg_dosR"] < 0.85,

            "DosR within expected range.",

            "DosR permanently saturated."

        )

        self.validator.report()

        TBCalibration.report(self)

        self.validate_biology()

    def validate_biology(self):

        if not self.debug_stats:
            return
        
        print("\n========== BIOLOGICAL VALIDATION ==========")

        if self.debug_stats["avg_dosR"] > 0.6:
            print("[PASS] DosR activated.")

        if self.debug_stats["avg_growth"] < 0.5:
            print("✓ Growth suppression observed.")

        if self.debug_stats["dormant_percent"] > 15:
            print("✓ Dormancy emerged.")

        if self.debug_stats["average_fitness"] > 0.2:
            print("✓ Population remained viable.")

        print("===========================================\n")
