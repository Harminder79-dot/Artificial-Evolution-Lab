import random
import math
from core.agent import Agent
from core.action import Action
from core.action_type import ActionType
from Brains.hardcoded_brain import HardcodedBrain
from core.memory import Memory

from configs.settings import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    STARTING_ENERGY,
    MOVE_ENERGY_BASE,
    FOOD_ENERGY,
    FOOD_RADIUS,
    REPRODUCTION_THRESH,
    REPRODUCTION_COST,
    MAX_AGE,
)

from agents.genome import random_genome

from evolution.mutation import gaussian_mutate


class Organism(Agent):

    def __init__(self, x, y, genome=None):

        import uuid

        self.id = str(uuid.uuid4())[:6]
        self.generation = 0
        self.parent_id = None
        self.children = []

        super().__init__()

        self.life_events = []
        self.brain = HardcodedBrain()
        self.memory = Memory()

        self.current_goal = "IDLE"

        self.drives = {

            "hunger": 0.5,
            "fear": 0.0,
            "curiosity": 0.5,
            "reproduction": 0.0
        }

        self.emotions = {

            "hunger": 0,
            "fear": 0,
            "curiosity": 0.5
        }


        self.self_beliefs = {

            "I am fast": 0,
            "I am hungry": 0,
            "I am weak": 0
        }

        self.x = x
        self.y = y

        self.genome = genome if genome else random_genome()

        self.energy = STARTING_ENERGY
        self.age = 0
        self.alive = True

        self.food_memory = []

    def move(self):

        speed = self.genome["speed"]

        vision = self.genome["vision_radius"]

        nearest_food = None
        nearest_distance = float("inf")

        for food in self.food_memory:

            fx, fy = food

            distance = math.hypot(self.x - fx, self.y - fy)

            if FOOD_RADIUS < distance < vision:

                if distance < nearest_distance:

                    nearest_food = food
                    nearest_distance = distance

        # move toward visible food
        if nearest_food:

            fx, fy = nearest_food

            dx = fx - self.x
            dy = fy - self.y

            length = math.hypot(dx, dy)

            if length > 0:

                dx /= length
                dy /= length

        else:
            # random wandering
            angle = random.uniform(0, 2 * math.pi)

            dx = math.cos(angle)
            dy = math.sin(angle)

        self.x += dx * speed
        self.y += dy * speed

        # world bounds
        self.x = max(0, min(WORLD_WIDTH, self.x))
        self.y = max(0, min(WORLD_HEIGHT, self.y))

        metabolism = self.genome["metabolism"]

        movement_cost = (
            MOVE_ENERGY_BASE
            * metabolism
            * (speed ** 1.7)
        )

        self.energy -= movement_cost
        self.energy -= 0.03

    def eat(self, food_list):

        for food in food_list[:]:

            fx, fy = food

            distance = math.hypot(self.x - fx, self.y - fy)

            if distance < FOOD_RADIUS:

                self.energy += FOOD_ENERGY
                self.add_event("Ate food")

                if self.energy > 400:
                    self.energy = 400

                food_list.remove(food)

                break

    def reproduce(self, organisms):

         if self.energy < REPRODUCTION_THRESH:
            return None

         nearby_count = 0

         for org in organisms:

            if org != self:

                distance = math.hypot(
                    self.x - org.x,
                    self.y - org.y
                )

                if distance < 50:
                    nearby_count += 1

         if nearby_count > 7:
            return None

         self.energy -= REPRODUCTION_COST

         child_genome = gaussian_mutate(self.genome)

         child = Organism(
            x=self.x + random.randint(-20, 20),
            y=self.y + random.randint(-20, 20),
            genome=child_genome
         )

         child.generation = (self.generation + 1)

         child.parent_id = (self.id)

         self.children.append(child.id)
         self.add_event(f"Reproduced -> {child.id}")

         return child
    
    def is_dead(self):
         if ( self.energy <= 0 or self.age >= MAX_AGE):

            self.add_event("Died")

            return True

         return False   
    
         return (
             self.energy <= 0
             or self.age >= MAX_AGE
         )

    def update(self, food_list, organisms):

          self.food_memory = food_list

          self.move()

          self.eat(food_list)

          self.age += 1

          return self.reproduce(organisms)
    
    def decide(self,environment):

        observation = (

            self.brain.perceive(self,environment)

        )

        return (

            self.brain.decide(self, observation)

        )
    
    def add_event( self, text):

        self.life_events.append(

            (

            self.age,

            text

            )

        )


        if len(

            self.life_events

        ) > 10:

            self.life_events.pop(0)

    def update_drives(self, predators=None):

        self.drives["hunger"] = (

            max(0, 1 - self.energy / 400)

        )


        self.drives["reproduction"] = (

            min(1, self.energy / 400)

        )


        self.drives["curiosity"] += 0.002

        self.drives["curiosity"] = min(1, self.drives["curiosity"])

        if predators:

            fear = 0

            for predator in predators:

                d = math.hypot(

                self.x - predator.x,

                self.y - predator.y

                )

                if d < 100:
                    fear += (100 - d) / 100


            self.drives["fear"] = min(1, fear)

        else:

            self.drives["fear"] *= 0.95