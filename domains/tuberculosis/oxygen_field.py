import numpy as np


class OxygenField:

    def __init__(self, width, height, resolution=10, diffusion_rate=1.0, decay_rate=0.005):

        self.width = width

        self.height = height

        self.resolution = resolution

        self.cols = width // resolution

        self.rows = height // resolution


        self.grid = np.ones(

            (

                self.rows,

                self.cols

            )

        )

        self.diffusion_rate = diffusion_rate

        self.decay_rate = decay_rate


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

        self.diffuse()

        self.grid *= (1.0 - self.decay_rate)

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

        self.grid = np.clip(self.grid, 0.0, 1.0)

    def consume_oxygen(self, bacteria):

        self.grid += 0.002

        for b in bacteria:

            c = int(b.x // self.resolution)
            r = int(b.y // self.resolution)

            if 0 <= r < self.rows and 0 <= c < self.cols:

                if b.state == b.ACTIVE:
                    consumption = 0.05

                elif b.state == b.REACTIVATING:
                    consumption = 0.035

                elif b.state == b.STRESSED:
                    consumption = 0.02

                else:   # DORMANT
                    consumption = 0.008

                self.grid[r, c] -= consumption

                self.grid[r, c] = max(
                    0.1,
                    self.grid[r, c]
                )

        self.grid = np.clip(self.grid, 0.0, 1.0)

    def diffuse(self):

        new_grid = self.grid.copy()

        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):

                neighbors = self.grid[r-1:r+2, c-1:c+2]

                neighbor_avg = (neighbors.sum() - self.grid[r, c]) / 8.0

                new_grid[r, c] += (
                    self.diffusion_rate
                    * 0.2
                    * (neighbor_avg - self.grid[r, c])
                )

        self.grid = new_grid