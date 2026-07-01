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

        self.vision_radius = 140

        self.speed = random.uniform(2.0, 3.2)

    def move(self):

        angle = random.uniform(0, 2*math.pi)


        self.x += 0.5 * math.cos(angle)

        self.y += 0.5 * math.sin(angle)

    def chase(self, bacteria):

        nearest = None
        nearest_dist = float("inf")

        for b in bacteria:

            if b.state == b.DEAD:
                continue

            dx = b.x - self.x
            dy = b.y - self.y

            dist = math.hypot(dx,dy)

            if dist < nearest_dist and dist < self.vision_radius:

                nearest = b
                nearest_dist = dist

        if nearest:

            dx = nearest.x - self.x
            dy = nearest.y - self.y

            dist = math.hypot(dx, dy)

            if dist > 0:

                speed = self.speed

                if dist < 40:
                    speed *= 1.5

                self.x += speed * dx / dist
                self.y += speed * dy / dist

            return nearest

        return None

    def infect(self):

        if self.state == Macrophage.HEALTHY:

            self.state = Macrophage.INFECTED

            self.intracellular_tb = 1

            print(

            f"Macrophage infected at "

            f"({self.x:.0f}, {self.y:.0f})"

        )

    def update(self, bacteria):

        self.age += 1

        target = self.chase(bacteria)

        if target:

            dist = math.hypot(
                target.x - self.x,
                target.y - self.y
            )

            if dist < 12:

                if self.state == Macrophage.HEALTHY:

                    if random.random() < 0.8:
                        target.state = target.DEAD

                    else:
                        self.infect()
                        target.state = target.DEAD

        if target is None:
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

            if random.random() < 0.03:
                self.intracellular_tb += 1

            if self.intracellular_tb > random.randint(18,35):

                self.state = Macrophage.DEAD

                print(

            f"Macrophage burst -> "

            f"{self.intracellular_tb} TB released"

        )

                return True

        else:

            self.signal_strength *= 0.98

        return False