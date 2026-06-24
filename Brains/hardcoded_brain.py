import random
import math
from core.brain import Brain
from core.action import Action
from core.action_type import ActionType

class HardcodedBrain(Brain):

    def perceive(self, organism, environment):

        nearest_food_distance = float("inf")

        nearest_food = None
        
        for food in environment.food:

            distance = (

                (organism.x - food[0])**2

                +

                (organism.y - food[1])**2

            )**0.5


            if distance < nearest_food_distance:

                nearest_food_distance = distance

                nearest_food = food

                organism.memory.remember("food_position",nearest_food, confidence=1.0)

        return {

    "energy":

    organism.energy,


    "age":

    organism.age,

    "nearest_food":

    nearest_food,


    "food_distance":

    nearest_food_distance,


    "remembered_food":

    organism.memory.recall(

        "food_position"

    )

}

    def decide(self, organism, observation):

        drives = organism.drives


        hunger = drives["hunger"]

        fear = drives["fear"]

        curiosity = drives["curiosity"]

        reproduction = drives["reproduction"]


        scores = {

            ActionType.SEARCH_FOOD:

                hunger,


            ActionType.EXPLORE:

                curiosity,


            ActionType.REPRODUCE:

                reproduction,


            ActionType.ESCAPE:

                fear

        }

        winner = max(scores, key=scores.get)

        organism.current_goal = ( winner.value)

        return Action(winner)