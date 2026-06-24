import random
import math


class ImmuneCell:

    def __init__(self,x,y):

        self.x = x

        self.y = y

        self.speed = 1.5


    def update(self,bacteria_list):

        nearest = None

        nearest_d = float("inf")


        for b in bacteria_list:

            if b.state != "ACTIVE":

                continue


            d = math.hypot(

                self.x - b.x,

                self.y - b.y

            )


            if d < nearest_d:

                nearest = b

                nearest_d = d


        if nearest:

            dx = nearest.x - self.x

            dy = nearest.y - self.y


            length = math.hypot(dx,dy)


            if length > 0:

                dx /= length

                dy /= length


            self.x += dx * self.speed

            self.y += dy * self.speed

    def move_towards(self,x,y):

        dx = x - self.x

        dy = y - self.y

        length = math.hypot(dx,dy)

        if length > 0:

            dx /= length

            dy /= length

            self.x += dx

            self.y += dy