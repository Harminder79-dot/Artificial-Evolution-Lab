import random

class Granuloma:

    HEALTHY = "HEALTHY"

    NECROTIC = "NECROTIC"

    RUPTURED = "RUPTURED"

    def __init__( self, x, y, radius):


        self.x = x

        self.y = y

        self.radius = radius

        self.age = 0

        self.state = Granuloma.HEALTHY

        self.necrotic = 0


    def update(self, dormant_tb):

        if self.state == Granuloma.RUPTURED:

            return False

        self.age += 1

        self.radius += dormant_tb * 0.005

        self.radius = min(

            self.radius,

            120

        )

        self.necrosis += dormant_tb * 0.0002

        self.necrosis = min(

            1,

            self.necrosis

        )


        if self.necrosis > 0.6:

            self.state = Granuloma.NECROTIC


        if self.state == Granuloma.NECROTIC:

            rupture_prob = (

                self.necrosis

                * 0.002

            )


            if random.random() < rupture_prob:

                self.state = Granuloma.RUPTURED

                return True


        return False