import numpy as np


class OxygenField:

    def __init__(

        self,

        width,

        height,

        resolution=10

    ):

        self.resolution = resolution


        self.cols = width // resolution

        self.rows = height // resolution


        self.grid = np.ones(

            (

                self.rows,

                self.cols

            )

        )


    def oxygen_at(

        self,

        x,

        y

    ):


        c = int(

            x //

            self.resolution

        )


        r = int(

            y //

            self.resolution

        )


        c = max(

            0,

            min(

                c,

                self.cols-1

            )

        )


        r = max(

            0,

            min(

                r,

                self.rows-1

            )

        )


        return self.grid[r,c]