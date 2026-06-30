from matplotlib import lines
import pygame
import math
from configs.settings import (

    WORLD_WIDTH,

    WORLD_HEIGHT

)

from domains.tuberculosis.bacteria import Bacteria
from domains.tuberculosis.granuloma import Granuloma
from domains.tuberculosis.macrophage import Macrophage


class TBRenderer:

    def __init__(self):

        self.children = []

        pygame.init()
        self.show_oxygen = True

        self.show_cytokines = True

        self.screen = pygame.display.set_mode(

            (

                WORLD_WIDTH,

                WORLD_HEIGHT

            )

        )


        pygame.display.set_caption(

            "TB Evolution Simulator"

        )


        self.font = pygame.font.SysFont("consolas", 20)


    def draw( self, bacteria, granulomas, tick, immune_cells, treatment, oxygen, cytokines, macrophages, selected_bacteria, bacteria_by_id, camera, paused, simulation_speed, debug_stats, history_size):

        
        self.screen.fill((15,18,22))

        if not debug_stats:

            debug_stats = {

                "avg_energy":0,
                "avg_growth":0,
                "avg_dormancy":0,
                "avg_stress":0,

                "avg_dosR":0,
                "avg_sigH":0,
                "avg_sigE":0,
                "avg_mprA":0,

                "avg_replication":0,
                "avg_virulence":0,
                "avg_dormancy_gene":0,

                "oxygen_min":0,
                "oxygen_max":0,

                "cytokine_max":0,

                "macrophages":0,
                "granulomas":0
            }

        if self.show_oxygen:
            
            self.draw_oxygen(oxygen, camera)

        if self.show_cytokines:

            self.draw_cytokines(cytokines, camera)

        for g in granulomas:

            gx, gy = camera.world_to_screen(
                g.x,
                g.y
            )

            center = (
                int(gx),
                int(gy)
            )

            radius = max(
                4,
                int(g.radius * camera.zoom)
            )

            # Outer glow
            pygame.draw.circle(
                self.screen,
                (110, 110, 110),
                center,
                radius + 8
            )

            # Main body
            if g.state == Granuloma.HEALTHY:
                body = (90, 90, 90)

            elif g.state == Granuloma.NECROTIC:
                body = (120, 60, 60)

            else:
                body = (170, 40, 40)

            pygame.draw.circle(
                self.screen,
                body,
                center,
                radius
            )

            # Dark necrotic core
            pygame.draw.circle(
                self.screen,
                (35, 35, 35),
                center,
                int(radius * 0.6)
            )

        for b in bacteria:

            fill_color = b.lineage_color

            if b.is_xdr:

                outline_color = (255,255,255)   # White

            elif b.is_mdr:

                outline_color = (255,0,255)      # Purple


            elif b.state == Bacteria.DORMANT:

                outline_color = (255,255,0)      # Yellow


            elif b.state == Bacteria.STRESSED:

                outline_color = (255,165,0)      # Orange


            elif b.state == Bacteria.REACTIVATING:

                outline_color = (0,255,255)      # Cyan


            else:

                outline_color = (0,255,0)        # Green

            x, y = camera.world_to_screen(b.x, b.y)

            x = int(x)

            y = int(y)

            radius = (
                4
                + min(b.age // 300, 2)
                + 0.4 * math.sin((tick + b.age) * 0.08)
            )

            radius = max(2, int(radius * camera.zoom))

            outline = max(1, int(2 * camera.zoom))
    # Inner circle

            pygame.draw.circle(

                self.screen,

                fill_color,

                (x,y),

                radius

            )


    # Outer ring

            pygame.draw.circle(

                self.screen,

                outline_color,

                (x,y),

                radius + 2,

                2

            )

        for immune in immune_cells:

            ix, iy = camera.world_to_screen(
                immune.x,
                immune.y
            )

            pygame.draw.circle(
                self.screen,
                (0,100,255),
                (int(ix), int(iy)),
                max(2, int(4 * camera.zoom))
            )

        y = 50
    
        for drug,active in treatment.items():
    
            if active:
                color = (0,255,0)
            else:
                color = (100,100,100)
    
            txt = self.font.render( drug, True, color)
    
            self.screen.blit( txt, (20,y))
    
            y += 25

        for m in macrophages:

            mx, my = camera.world_to_screen(
                m.x,
                m.y
            )

            x = int(mx)
            y = int(my)

            if m.state == Macrophage.HEALTHY:
                fill = (80,170,255)

            elif m.state == Macrophage.INFECTED:
                fill = (255,180,40)

            else:
                fill = (180,60,255)

            pygame.draw.circle(self.screen, (40,40,40), (x,y), 9)
            pygame.draw.circle(self.screen, fill, (x,y), 8)
            pygame.draw.circle(self.screen, (255,255,255), (x,y), 8, 1)

        legend = [

            ("ACTIVE",(0,255,0)),

            ("STRESSED",(255,165,0)),

            ("DORMANT",(255,255,0)),

            ("REACTIVATING",(0,255,255)),

            ("MDR",(255,0,255)),

            ("XDR",(255,255,255)),

            ("NECROTIC",(120,60,60)),

            ("RUPTURED",(255,0,0))

        ]


        y = 80


        for name,color in legend:

            pygame.draw.circle(

                self.screen,

                color,

                (30,y),

                6

            )


            txt = self.font.render( name, True, (255,255,255))

            self.screen.blit( txt, (45,y-10))


            y += 25
        
        if selected_bacteria:

            sx, sy = camera.world_to_screen(
                selected_bacteria.x,
                selected_bacteria.y
            )

            pygame.draw.circle(
                self.screen,
                (255,255,255),
                (int(sx), int(sy)),
                max(5, int(10 * camera.zoom)),
                2
            )

        if selected_bacteria:

            self.draw_lineage_links(

                selected_bacteria,
                bacteria_by_id,
                camera

            )

        panel = pygame.Surface((300, WORLD_HEIGHT), pygame.SRCALPHA)

        panel.fill((20, 20, 25, 190))

        self.screen.blit(
            panel,
            (WORLD_WIDTH - 300, 0)
        )

        # ---------------- Simulation Statistics ----------------

        active = sum(
            b.state == Bacteria.ACTIVE
            for b in bacteria
        )

        dormant = sum(
            b.state == Bacteria.DORMANT
            for b in bacteria
        )

        stressed = sum(
            b.state == Bacteria.STRESSED
            for b in bacteria
        )

        mdr = sum(
            b.is_mdr
            for b in bacteria
        )

        xdr = sum(
            b.is_xdr
            for b in bacteria
        )

        stats = [

            ("TB EVOLUTION", (255,255,255)),

            ("", (255,255,255)),

            (f"Tick : {tick}", (200,200,200)),

            (f"Population : {len(bacteria)}", (255,255,255)),

            (
                f"Avg Fitness : "
                f"{debug_stats['average_fitness']:.2f}",
                (120,255,120)
            ),

            (
                f"Best Fitness : "
                f"{debug_stats['best_fitness']:.2f}",
                (255,255,120)
            ),

            (
                f"Best Gen : "
                f"{debug_stats['best_generation']}",
                (255,220,120)
            ),

            (
                f"ACTIVE : "
                f"{debug_stats['active_percent']:.1f}%",
                (0,255,0)
            ),

            (
                f"STRESSED : "
                f"{debug_stats['stressed_percent']:.1f}%",
                (255,180,0)
            ),

            (
                f"DORMANT : "
                f"{debug_stats['dormant_percent']:.1f}%",
                (100,200,255)
            ),

            (
                f"REACTIVATING : "
                f"{debug_stats['reactivating_percent']:.1f}%",
                (255,100,255)
            ),

            (f"Granulomas : {len(granulomas)}", (255,255,255)),

            (f"Macrophages : {len(macrophages)}", (255,255,255)),

            (f"Immune : {len(immune_cells)}", (255,255,255)),

            ("", (255,255,255)),

            (f"ACTIVE : {active}", (0,255,0)),

            (f"DORMANT : {dormant}", (255,255,0)),

            (f"STRESSED : {stressed}", (255,165,0)),

            ("", (255,255,255)),

            (f"MDR : {mdr}", (255,0,255)),

            (f"XDR : {xdr}", (255,255,255)),

            (f"Paused : {paused}", (255,255,255)),

            (f"Speed : {simulation_speed}x", (0,255,255)),

        ]

        x = WORLD_WIDTH - 285

        y = 20

        for text, color in stats:

            surface = self.font.render(
                text,
                True,
                color
            )

            self.screen.blit(
                surface,
                (x, y)
            )

            y += 24

        # ---------- DEBUG PANEL ----------

        y += 20

        title = self.font.render(
            "DEBUG",
            True,
            (255,180,0)
        )

        self.screen.blit(
            title,
            (x,y)
        )

        y += 30

        debug = [

            (
                f"Avg Energy : "
                f"{debug_stats['avg_energy']:.2f}",
                (220,220,220)
            ),

            (
                f"Avg Growth : "
                f"{debug_stats['avg_growth']:.2f}",
                (0,255,0)
            ),

            (
                f"Avg Dormancy : "
                f"{debug_stats['avg_dormancy']:.2f}",
                (255,255,0)
            ),

            (
                f"Avg Stress : "
                f"{debug_stats['avg_stress']:.2f}",
                (255,120,0)
            ),

            (
                f"dosR : "
                f"{debug_stats['avg_dosR']:.2f}",
                (100,255,255)
            ),

            (
                f"sigH : "
                f"{debug_stats['avg_sigH']:.2f}",
                (255,150,255)
            ),

            (
                f"sigE : "
                f"{debug_stats['avg_sigE']:.2f}",
                (255,180,120)
            ),

            (
                f"dosR σ : "
                f"{debug_stats['dosR_std']:.3f}",
                (120,255,255)
            ),

            (
                f"sigH σ : "
                f"{debug_stats['sigH_std']:.3f}",
                (255,150,255)
            ),

            (
                f"sigE σ : "
                f"{debug_stats['sigE_std']:.3f}",
                (255,180,120)
            ),

            (
                f"mprA : "
                f"{debug_stats['avg_mprA']:.2f}",
                (200,255,150)
            ),

            (
                f"Replication : "
                f"{debug_stats['avg_replication']:.4f}",
                (200,200,255)
            ),

            (
                f"Virulence : "
                f"{debug_stats['avg_virulence']:.2f}",
                (255,100,100)
            ),

            (
                f"Dormancy Gene : "
                f"{debug_stats['avg_dormancy_gene']:.2f}",
                (255,255,120)
            ),

            (
                f"O2 Min : "
                f"{debug_stats['oxygen_min']:.2f}",
                (150,255,255)
            ),

            (
                f"O2 Max : "
                f"{debug_stats['oxygen_max']:.2f}",
                (150,255,255)
            ),

            (
                f"O2 Avg : "
                f"{debug_stats['oxygen_average']:.2f}",
                (120,255,255)
            ),

            (
                f"O2 Std : "
                f"{debug_stats['oxygen_std']:.2f}",
                (120,255,255)
            ),

            (
                f"Hypoxic TB : "
                f"{debug_stats['hypoxic_bacteria']}",
                (255,220,120)
            ),

            (
                f"Cytokine Max : "
                f"{debug_stats['cytokine_max']:.2f}",
                (255,120,0)
            ),

            (
                f"Cytokine Avg : "
                f"{debug_stats['cytokine_average']:.2f}",
                (255,170,80)
            ),

            (
                f"Cytokine Std : "
                f"{debug_stats['cytokine_std']:.2f}",
                (255,170,80)
            ),

            (
                f"Hotspots : "
                f"{debug_stats['cytokine_hotspots']}",
                (255,220,120)
            ),

            (
                f"Infected Mac : "
                f"{debug_stats['infected_macrophages']}",
                (255,120,120)
            ),

            (
                f"Macrophages : "
                f"{debug_stats['macrophages']}",
                (120,255,120)
            ),

            (
                f"Granulomas : "
                f"{debug_stats['granulomas']}",
                (220,220,220)
            ),

            (
                f"Oldest : "
                f"{debug_stats['oldest_age']}",
                (180,255,180)
            ),

            (
                f"Largest Family : "
                f"{debug_stats['largest_family']}",
                (255,180,255)
            ),

            (
                f"Living Lineages : "
                f"{debug_stats['living_lineages']}",
                (150,255,255)
            ),

            (
                f"Avg Generation : "
                f"{debug_stats['average_generation']:.2f}",
                (255,255,180)
            ),

            (
                f"Unique Genomes : "
                f"{debug_stats['unique_genomes']}",
                (255,180,120)
            ),

            (
                f"Avg Mutations : "
                f"{debug_stats['average_mutations']:.2f}",
                (180,255,180)
            ),

            (
                f"History : {history_size}",
                (180,180,255)
            ),

            (
                f"Peak Pop : {debug_stats['peak_population']}",
                (220,220,220)
            ),

            (
                f"Lowest Pop : {debug_stats['lowest_population']}",
                (220,220,220)
            ),

            (
                f"Runtime : {debug_stats['runtime']:.1f}s",
                (220,220,220)
            ),

        ]

        for text,color in debug:

            surface = self.font.render(
                text,
                True,
                color
            )

            self.screen.blit(
                surface,
                (x,y)
            )

            y += 22

        if selected_bacteria:

            self.draw_info_panel(

                selected_bacteria

            )

        if self.show_oxygen:

            text = self.font.render(
                f"O2 min:{oxygen.grid.min():.2f} max:{oxygen.grid.max():.2f}",
                True,
                (255,255,255)
            )

            self.screen.blit(
                text,
                (20, WORLD_HEIGHT - 60)
            )

        if self.show_cytokines:

            text = self.font.render(
                f"Cytokine max:{cytokines.grid.max():.2f}",
                True,
                (255,120,0)
            )

            self.screen.blit(
                text,
                (20, WORLD_HEIGHT - 30)
            )

        pygame.display.flip()


    def draw_oxygen(self, oxygen, camera):

        cell = oxygen.resolution

        overlay = pygame.Surface(
            (WORLD_WIDTH, WORLD_HEIGHT),
            pygame.SRCALPHA
        )

        for row in range(oxygen.rows):

            for col in range(oxygen.cols):

                value = oxygen.grid[row, col]

                red = int((1 - value) * 255)
                green = int(value * 255)

                color = (
                    red,
                    green,
                    40,
                    140
                )

                x, y = camera.world_to_screen(
                    col * cell,
                    row * cell
                )

                size = cell * camera.zoom

                pygame.draw.rect(
                    overlay,
                    color,
                    (x, y, size, size)
                )

        self.screen.blit(
            overlay,
            (0, 0)
        )

    def draw_info_panel(self, b):

        x = WORLD_WIDTH - 285

        y = 360

        scores = b.grn.last_scores

        lines = [

            f"ID : {b.id}",

            f"Parent : {b.parent_id}",

            f"Generation : {b.generation}",

            f"Founder : {b.founder_id}",

            f"Children : {len(b.children)}",

            f"Birth Tick : {b.birth_tick}",

            f"Age : {b.age}",

            f"Fitness : {b.fitness:.2f}",

            f"State : {b.state}",

            f"Growth : {b.grn.current_phenotype['growth_factor']:.2f}",

            f"Stress : {b.grn.current_phenotype['stress_tolerance']:.2f}",

            f"Dormancy : {b.grn.current_phenotype['dormancy']:.2f}",

            "",

            "State Scores",

            f"ACTIVE : {scores['ACTIVE']:.2f}",

            f"DORMANT : {scores['DORMANT']:.2f}",

            f"STRESSED : {scores['STRESSED']:.2f}",

            f"REACTIVATING : {scores['REACTIVATING']:.2f}",

            "",

            "Genome"

        ]

        lines.append("")
        lines.append("GRN")

        for gene,value in b.genome.items():
                
            if isinstance(value, dict):

                line = f"{gene}: {len(value)} regulators"

            else:

                line = f"{gene}: {value:.3f}"

            lines.append(line)

        lines.append("")

        lines.append("Mutations")


        if len(b.mutations) == 0:

            lines.append(

                "None"

            )

        else:

            for m in b.mutations[-5:]:

                lines.append(

                    f"G{m['generation']} "

                    f"{m['gene']} "

                    f"{m['delta']:+.3f}"

                )


        for line in lines:

            text = self.font.render(

                line,

                True,

                (255,255,255)

            )

            self.screen.blit(

                text,

                (x,y)

            )

            y += 25

    def draw_lineage_links(self, selected, bacteria_by_id, camera):
        parent_id = selected.parent_id


        if parent_id:

            parent = bacteria_by_id.get(parent_id)


            if parent:

                px, py = camera.world_to_screen(
                    parent.x,
                    parent.y
                )

                sx, sy = camera.world_to_screen(
                    selected.x,
                    selected.y
                )

                pygame.draw.line(
                    self.screen,
                    (180,180,180),
                    (int(px), int(py)),
                    (int(sx), int(sy)),
                    2
                )

        for child_id in selected.children:

            child = bacteria_by_id.get(child_id)


            if child:

                sx, sy = camera.world_to_screen(
                    selected.x,
                    selected.y
                )

                cx, cy = camera.world_to_screen(
                    child.x,
                    child.y
                )

                pygame.draw.line(
                    self.screen,
                    (100,255,255),
                    (int(sx), int(sy)),
                    (int(cx), int(cy)),
                    1
                )

    def gene_color(value):

        intensity = int(value * 255)

        return (intensity, 255-intensity, 80)
    
    def draw_cytokines(self, cytokines, camera):

        cell = cytokines.resolution

        for row in range(cytokines.rows):

            for col in range(cytokines.cols):

                value = cytokines.grid[row, col]

                # Ignore tiny values
                if value < 0.005:
                    continue

                cx, cy = camera.world_to_screen(

                    col * cell + cell // 2,
                    row * cell + cell // 2

                )

                radius = max(4, int(value * 30))

                radius = max(4, int(radius * camera.zoom))

                alpha = min(int(value * 220), 220)

                glow = pygame.Surface(
                    (radius * 4, radius * 4),
                    pygame.SRCALPHA
                )

                pygame.draw.circle(
                    glow,
                    (255, 60, 0, alpha),
                    (radius * 2, radius * 2),
                    radius
                )

                self.screen.blit(
                    glow,
                    (
                        cx - radius * 2,
                        cy - radius * 2
                    )
                )