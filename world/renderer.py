import pygame
from configs.settings import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    BG_COLOR,
    FOOD_COLOR,
)

class Renderer:

    def __init__(self):

        pygame.init()
        self.font = pygame.font.SysFont("consolas",18)

        self.screen = pygame.display.set_mode(
            (WORLD_WIDTH, WORLD_HEIGHT)
        )

        pygame.display.set_caption(
            "Artificial Evolution Laboratory"
        )

        self.font = pygame.font.SysFont(None, 22)


    def draw_food(self, food_list):

        for food in food_list:

            pygame.draw.circle(
                self.screen,
                FOOD_COLOR,
                (int(food[0]), int(food[1])),
                3
            )

    def draw_organisms(self, organisms):

     for organism in organisms:

        x = int(organism.x)
        y = int(organism.y)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        distance = (

            (mouse_x - x)**2 +

            (mouse_y - y)**2

        )**0.5

        if distance < 10:

            self.draw_tooltip(organism)

        # Genome traits
        speed = organism.genome["speed"]
        vision = organism.genome["vision_radius"]
        metabolism = organism.genome["metabolism"]

        # Convert traits into RGB
        r = min(255, int(speed * 40))

        g = min(255, int(vision * 2))

        b = min(255, int((2 - metabolism) * 120))

        color = (r, g, b)

        pygame.draw.circle(
            self.screen,
            color,
            (x, y),
            max(3, int(organism.genome["size"] * 0.7))
        )

    def draw(self, organisms, predators, food, tick, selected_organism):

        self.screen.fill(BG_COLOR)

        self.draw_food(food)

        self.draw_organisms(organisms)

        self.draw_predators(predators)

        self.draw_info_panel(

            selected_organism

        )

        pygame.display.flip()

    def draw_predators(self, predators):

        for predator in predators:

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (int(predator.x), int(predator.y)),
                8
            )

    def draw_tooltip(self, organism):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        lines = [

            f"Energy: {organism.energy:.1f}",

            f"Age: {organism.age}",

            f"Speed: {organism.genome['speed']:.2f}",

            f"Vision: {organism.genome['vision_radius']:.2f}",

            f"Metabolism: {organism.genome['metabolism']:.2f}",

            f"Size: {organism.genome['size']:.2f}",

            f"Goal : {organism.current_goal}"

        ]

        y_offset = 0

        for line in lines:

            text = self.font.render(line, True, (255,255,255))
            
            self.screen.blit( 
                text,
                (
                    mouse_x + 15, 
                    mouse_y + y_offset
                    
                )
            )

            y_offset += 20

    def draw_info_panel(self,organism):

        if organism is None:

            return


        lines = [

        f"Age : {organism.age}",

        f"Energy : {organism.energy:.1f}",

        f"Speed : {organism.genome['speed']:.2f}",

        f"Vision : {organism.genome['vision_radius']:.2f}",

        f"Metabolism : {organism.genome['metabolism']:.2f}",

        f"Size : {organism.genome['size']:.2f}"

        ]

        lines.append("")

        lines.append("Drives")

        for drive, value in organism.drives.items():

            lines.append(

                f"{drive}: "

                f"{value:.2f}"

            )

        lines.append("Recent Events")
        for age,event in (

            organism.life_events[-3:]

        ):

            lines.append(

                f"{age}: {event}"

            )


        remembered_food = (

            organism.memory.recall(

                "food_position"

            )

        )

        if remembered_food:
            lines.append(

                f"Memory : {remembered_food}"

            )

        else:
            lines.append(

                "Memory : Unknown"
                
            )

        y = 20

        for line in lines:

            surface = self.font.render(line,True,(255,255,255))

            self.screen.blit(surface,(20,y))

            y += 25


    def draw_bar(self, screen, x, y, width, height, value):

        pygame.draw.rect(screen, (80,80,80), (x,y,width,height))
        pygame.draw.rect(screen, (0,220,0),(x, y, width * value, height))