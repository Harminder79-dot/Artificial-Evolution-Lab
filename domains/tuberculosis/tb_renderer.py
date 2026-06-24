import pygame
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
        self.show_oxygen = False

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


    def draw( self, bacteria, granulomas, tick, immune_cells, treatment, oxygen, macrophages, selected_bacteria, bacteria_by_id):


        self.screen.fill((10,10,10))
        if self.show_oxygen:

            self.draw_oxygen(

                oxygen

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


            x = int(b.x)

            y = int(b.y)


    # Inner circle

            pygame.draw.circle(

                self.screen,

                fill_color,

                (x,y),

                4

            )


    # Outer ring

            pygame.draw.circle(

                self.screen,

                outline_color,

                (x,y),

                6,

                2

            )

        for g in granulomas:

            if g.state == Granuloma.HEALTHY:

                color = (150,150,150)

            elif g.state == Granuloma.NECROTIC:

                color = (120,60,60)

            else:

                color = (255,0,0)

            pygame.draw.circle(

            self.screen,

            color,

            (

                int(g.x),

                int(g.y)

            ),

            int(g.radius),

            2

        )

        for immune in immune_cells:

            pygame.draw.circle(

                self.screen,

                (0,100,255),

                (

                    int(immune.x),

                    int(immune.y)

                ),

                4

            )

        text = self.font.render(

            f"Tick : {tick}",

            True,

            (255,255,255)

        )


        self.screen.blit(

            text,

            (20,20)

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

            if m.state == Macrophage.HEALTHY:

                color = (0,150,255)

            else:

                color = (255,0,255)

            pygame.draw.circle(self.screen, color, (int(m.x), int(m.y)), 6)

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

            pygame.draw.circle(

                self.screen,

                (255,255,255),

                (

                    int(selected_bacteria.x),

                    int(selected_bacteria.y)

                ),

                10,

                2

            )

        if selected_bacteria:

            self.draw_lineage_links(

                selected_bacteria,

                bacteria_by_id

            )

        if selected_bacteria:

            self.draw_info_panel(

                selected_bacteria

            )

        pygame.display.flip()


    def draw_oxygen(self, oxygen):

        cell = oxygen.resolution


        for row in range(oxygen.rows):

            for col in range(oxygen.cols):

                value = oxygen.grid[row,col]


                intensity = int(value * 255)


                color = (intensity, intensity, intensity)


                pygame.draw.rect(self.screen, color, (

                    col * cell,

                    row * cell,

                    cell,

                    cell

                    )

                )

    def draw_info_panel(self, b):

        x = WORLD_WIDTH - 300

        y = 20


        lines = [

            f"ID : {b.id}",

            f"Parent : {b.parent_id}",

            f"Generation : {b.generation}",

            f"Age : {b.age}",

            f"State : {b.state}",

            "",

            "Genome"

        ]


        for gene,value in b.genome.items():

            lines.append(

                f"{gene} : {value:.2f}"

            )


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

    def draw_lineage_links(self, selected, bacteria_by_id):
        parent_id = selected.parent_id


        if parent_id:

            parent = bacteria_by_id.get(parent_id)


            if parent:

                pygame.draw.line(

                    self.screen,

                    (180,180,180),

                    (

                        int(parent.x),

                        int(parent.y)

                    ),

                    (

                        int(selected.x),

                        int(selected.y)

                    ),

                    2

                )

        for child_id in selected.children:

            child = bacteria_by_id.get(child_id)


            if child:

                pygame.draw.line(

                    self.screen,

                    (100,255,255),

                    (

                        int(selected.x),

                        int(selected.y)

                    ),

                    (

                        int(child.x),

                        int(child.y)

                    ),

                    1

                )