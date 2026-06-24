import random
import math

class Macrophage:

    HEALTHY = "HEALTHY"

    INFECTED = "INFECTED"

    DEAD = "DEAD"


    def __init__(self, x, y):

        self.x = x

        self.y = y

        self.exhaustion = 0

        self.state = Macrophage.HEALTHY

        self.intracellular_tb = 0

        self.age = 0

        self.signal_strength = 0

    def move(self):

        angle = random.uniform(0, 2*math.pi)


        self.x += 0.5 * math.cos(angle)

        self.y += 0.5 * math.sin(angle)

    def infect(self):

        if self.state == Macrophage.HEALTHY:

            self.state = Macrophage.INFECTED

            self.intracellular_tb = 1

            print(

            f"Macrophage infected at "

            f"({self.x:.0f}, {self.y:.0f})"

        )

    def update(self):

        self.age += 1

        self.move()

        if self.state == Macrophage.INFECTED:

            self.exhaustion += 0.001

            self.exhaustion = min(

                1,

                self.exhaustion

            )

            self.signal_strength += 0.02

            self.signal_strength = min(

                1,

                self.signal_strength

            )

            if random.random() < 0.01:

                self.intracellular_tb += 1


            if self.intracellular_tb > 25:

                self.state = Macrophage.DEAD

                print(

            f"Macrophage burst -> "

            f"{self.intracellular_tb} TB released"

        )

                return True

        else:

            self.signal_strength *= 0.98

        return False