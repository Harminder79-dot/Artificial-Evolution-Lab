from core import environment
from core.rule import Rule
from core.action_type import ActionType
import math
import random
from configs.settings import (WORLD_WIDTH, WORLD_HEIGHT)

class MoveRule(Rule):

    def apply(self, environment,):
        angle = 0

        for organism, action in environment.actions:

            if action.type not in [

                ActionType.EXPLORE,

                ActionType.SEARCH_FOOD,

                ActionType.ESCAPE

            ]:

                continue

            speed = organism.genome["speed"]


# SEARCH FOOD

            if action.type == ActionType.SEARCH_FOOD:

                target = organism.memory.recall("food_position")

                if target:

                    fx, fy = target


                    dx = fx - organism.x

                    dy = fy - organism.y


                    length = math.hypot(

                        dx,

                        dy

                    )


                    if length > 0:

                        dx /= length

                        dy /= length

                    else:

                        dx = 0

                        dy = 0


                else:

                    angle = random.uniform(

                    0,

                    2 * math.pi

                )

                    dx = math.cos(angle)

                    dy = math.sin(angle)



# EXPLORE

            elif action.type == ActionType.EXPLORE:

                angle = random.uniform(

                    0,

                    2 * math.pi

                )

                dx = math.cos(angle)

                dy = math.sin(angle)



# ESCAPE

            elif action.type == ActionType.ESCAPE:

                nearest = None

                nearest_distance = float("inf")


                for predator in environment.predators:

                    distance = math.hypot(

                        organism.x - predator.x,

                        organism.y - predator.y

                    )


                    if distance < nearest_distance:

                        nearest = predator

                        nearest_distance = distance


                if nearest:

                    dx = organism.x - nearest.x

                    dy = organism.y - nearest.y


                    length = math.hypot(

                        dx,

                        dy

                    )


                    if length > 0:

                        dx /= length

                        dy /= length

                    else:

                        dx = 0

                        dy = 0

                else:

                    angle = random.uniform(

                        0,

                        2 * math.pi

                    )

                    dx = math.cos(angle)

                    dy = math.sin(angle)



            organism.x += dx * speed

            organism.y += dy * speed


            organism.x = max(

                0,

                min(

                    WORLD_WIDTH,

                    organism.x

                )

            )


            organism.y = max(

                0,

                min(

                    WORLD_HEIGHT,

                    organism.y

                )

            )