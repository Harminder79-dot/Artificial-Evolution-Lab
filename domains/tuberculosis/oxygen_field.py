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
    
    def update(self, granulomas):

        self.grid[:] = 1.0

        for g in granulomas:

            cx = int(g.x // self.resolution)
            cy = int(g.y // self.resolution)

            radius = int(g.radius // self.resolution)

            for r in range(
                max(0, cy-radius),
                min(self.rows, cy+radius)
            ):

                for c in range(
                    max(0, cx-radius),
                    min(self.cols, cx+radius)
                ):

                    dx = c - cx
                    dy = r - cy

                    dist = (dx*dx + dy*dy) ** 0.5

                    if dist <= radius:

                        reduction = 0.8 * (
                            1 - dist/max(radius,1)
                        )

                        self.grid[r,c] = max(
                            0.05,
                            self.grid[r,c] - reduction
                        )

    def consume_oxygen(self, bacteria):

        self.grid[:] = np.minimum(
            self.grid + 0.0001,
            1.0
        )

        for b in bacteria:

            c = int(b.x // self.resolution)
            r = int(b.y // self.resolution)

            if 0 <= r < self.rows and 0 <= c < self.cols:

                self.grid[r, c] -= 0.05

                self.grid[r, c] = max(
                    0.1,
                    self.grid[r, c]
                )