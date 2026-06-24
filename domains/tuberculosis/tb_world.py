import random
import math
import pygame
from domains.tuberculosis.granuloma import Granuloma
from domains.tuberculosis.immune_cell import ImmuneCell
from domains.tuberculosis.oxygen_field import OxygenField
from configs.settings import (

    WORLD_WIDTH,

    WORLD_HEIGHT,

    FPS

)
from domains.tuberculosis.macrophage import Macrophage
from domains.tuberculosis.bacteria import Bacteria
from domains.tuberculosis.tb_renderer import TBRenderer


class TBWorld:


    def __init__(self):

        self.tick = 0

        self.treatment = {

            "INH": False,

            "RIF": False,

            "PZA": False,

            "EMB": False

        }

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

        self.mdr_history = []

        self.renderer = TBRenderer()

        self.selected_bacteria = None

        self.oxygen = OxygenField(WORLD_WIDTH, WORLD_HEIGHT)

        self.immune_cells = []

        for _ in range(40):

            cell = ImmuneCell(

                random.randint(0,WORLD_WIDTH),

                random.randint(0,WORLD_HEIGHT)

            )

            self.immune_cells.append(cell)

        for _ in range(25):


            b = Bacteria(

                WORLD_WIDTH//2 + random.randint(-40,40),

                WORLD_HEIGHT//2 + random.randint(-40,40)

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


        for _ in range(60):

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

        self.oxygen.update(self.granulomas)
        self.oxygen.consume_oxygen(self.bacteria)
        new_granuloma_bacteria = []
        self.tick += 1
        reproduction_added = 0
        granuloma_added = 0
        macrophage_added = 0

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

            print(
                "Granuloma dormant:",
                dormant_tb
            )

            burst = g.update(dormant_tb)

            if burst:

                print(
                    f"GRANULOMA RUPTURE @ {self.tick}"
                )

                print(
                    f"Population before rupture:"
                    f"{len(self.bacteria)}"
                )

                for _ in range(20):

                    b = Bacteria(

                        g.x +

                        random.randint(-40,40),

                        g.y +

                        random.randint(-40,40)

                    )

                    b.state = Bacteria.ACTIVE

                    new_granuloma_bacteria.append(b)

                    granuloma_added += 1

                    self.lineages[b.id] = {

                        "parent": None,

                        "children": []

                    }

          self.bacteria.extend(new_granuloma_bacteria)

          if len(new_granuloma_bacteria) > 0:

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

                        print("TB KILLED")

                    else:

                        m.infect()

                        b.state = Bacteria.DEAD

                        print("MACROPHAGE INFECTED")

                        print(
                            f"INFECTED MACROPHAGE "
                            f"TB:{b.id}"
                        )

                    break

        if self.tick == 2000:

            self.treatment["INH"] = True
            self.treatment["RIF"] = True
            self.treatment["PZA"] = True
            self.treatment["EMB"] = True


        if self.tick == 5000:

            self.treatment["INH"] = False
            self.treatment["RIF"] = False
            self.treatment["PZA"] = False
            self.treatment["EMB"] = False

        newborns = []
        births = 0

        for b in self.bacteria[:]:

            b.update(self.oxygen)

            self.apply_treatment(b)

            if b.state == Bacteria.DEAD:

                continue

            child = b.reproduce()


            if child:
                
                births += 1
                reproduction_added += 1
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

            print(
                f"Tick:{self.tick} "
                f"Births:{births} "
                f"Newborns:{len(newborns)} "
                f"Pop:{len(self.bacteria)}",
                flush=True
            )

            self.bacteria_by_id = {

                b.id : b

                for b in self.bacteria

            }

        new_bacteria = []

        for m in self.macrophages:

            burst = m.update(self.bacteria)

            if burst:

                print(

                    f"Macrophage burst -> "

                    f"{m.intracellular_tb} TB released"

                )

                for _ in range(m.intracellular_tb):
                    
                    print(f"RUPTURE @ Tick {self.tick}")

                    print(
                        f"Population before rupture: "
                        f"{len(self.bacteria)}"
                    )

                    angle = random.uniform(0, 2*math.pi)

                    radius = random.uniform(5,40)

                    child = Bacteria(

                        m.x + radius*math.cos(angle),

                        m.y + radius*math.sin(angle)
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

        MAX_BACTERIA = 2000

        if len(self.bacteria) < MAX_BACTERIA:
            self.bacteria.extend(new_bacteria)

        macrophage_added = len(new_bacteria)

        if len(new_bacteria) > 0:

            print(
                f"Macrophages added "
                f"{len(new_bacteria)} bacteria"
            )

        self.bacteria = [

            b

            for b in self.bacteria

            if b.state

            !=

            Bacteria.DEAD

        ]

        self.macrophages = [

            m

            for m in self.macrophages

            if m.state != Macrophage.DEAD

        ]

        print(
            f"Added -> "
            f"Repro:{reproduction_added} "
            f"Gran:{granuloma_added} "
            f"Macro:{macrophage_added}"
        )

        if self.tick % 100 == 0:

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


            print(
                "Oxygen:",
                self.oxygen.grid.min(),
                self.oxygen.grid.max(),
                min(self.oxygen.grid.flatten()),
                max(self.oxygen.grid.flatten())
            )

            sample = random.choice(self.bacteria)

            o2 = self.oxygen.oxygen_at(
                sample.x,
                sample.y
            )

            print("Sample oxygen:", round(o2, 2))

            avg_inh = sum(

                b.genome["inh_resistance"]

                for b in self.bacteria

            ) / max(

                1,

                len(self.bacteria)

            )


            avg_rif = sum(

                b.genome["rif_resistance"]

                for b in self.bacteria

            ) / max(

                1,

                len(self.bacteria)

            )

            lineage_sizes = {}

            for b in self.bacteria:

                founder = self.lineage_stats[b.id]["founder"]

                lineage_sizes[founder] = (
                    lineage_sizes.get(founder, 0) + 1
                )

            if lineage_sizes:

                biggest = max(
                    lineage_sizes,
                    key=lineage_sizes.get
                )


                print(
                    f"Largest Lineage: {biggest}"
                    f" | Size: {lineage_sizes[biggest]}"
                )


            mdr_count = sum(

                1

                for b in self.bacteria

                if b.is_mdr

            )


            self.avg_inh_history.append(

                avg_inh

            )

            self.avg_rif_history.append(

                avg_rif

            )

            avg_mdr = sum(

                1

                for b in self.bacteria

                if b.is_mdr

            )

            avg_xdr = sum(

                1

                for b in self.bacteria

                if b.is_xdr

            )

            print(

                f"MDR:{avg_mdr} "

                f"XDR:{avg_xdr}"

            )

            self.population_history.append(

                len(self.bacteria)

            )

            self.mdr_history.append(

                mdr_count
            )

            active = sum(

                1

                for b in self.bacteria

                if b.state == "ACTIVE"

            )


            dormant = sum(

                1

                for b in self.bacteria

                if b.state == "DORMANT"

            )

            xdr = sum(

                1

                for b in self.bacteria

                if b.is_xdr

            )
            if len(self.bacteria) > 0:
                max_rep = max(
                    b.genome["replication_rate"]
                    for b in self.bacteria
                )

                avg_rep = sum(
                    b.genome["replication_rate"]
                    for b in self.bacteria
                ) / len(self.bacteria)

            else: 
                max_rep = 0
                avg_rep = 0

            print(
                f"Max Rep:{max_rep:.6f}"
            )

            print(
                f"Avg Rep:{avg_rep:.6f}"
            )

            print(

                f"Tick:{self.tick}"

                f" | Pop:{len(self.bacteria)}"

                f" | MDR:{mdr_count}"

                f" | XDR:{xdr}"

                f" | Avg INH:{avg_inh:.2f}"

                f" | Avg RIF:{avg_rif:.2f}"

            )

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

            strongest = None

            signal = 0


            for m in self.macrophages:

                if m.signal_strength > signal:

                    signal = m.signal_strength

                    strongest = m


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

    def run(self):


        clock = pygame.time.Clock()


        running = True


        while running:


            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_o:

                        self.renderer.show_oxygen = (

                            not self.renderer.show_oxygen

                        )
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        mx, my = pygame.mouse.get_pos()

                        self.selected_bacteria = None


                        for b in self.bacteria:

                            d = math.hypot(

                                b.x - mx,

                                b.y - my

                            )

                            if d < 8:

                                self.selected_bacteria = b

                                break

                if event.type == pygame.QUIT:

                    running = False


            self.update()


            self.renderer.draw(

                self.bacteria,
                self.granulomas,
                self.tick,
                self.immune_cells,
                self.treatment,
                self.oxygen,
                self.macrophages,
                self.selected_bacteria,
                self.bacteria_by_id
            )

            clock.tick(

                FPS

            )


        pygame.quit()

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

            prob = 0.002 * (

                1 -

                b.genome["inh_resistance"]

            )

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