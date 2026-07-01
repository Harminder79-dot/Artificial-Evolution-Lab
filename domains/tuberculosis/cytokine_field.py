import numpy as np


class CytokineField:

    def __init__(
        self,
        width,
        height,
        resolution=10,
        diffusion_rate=0.20,
        decay_rate=0.01
    ):

        self.width = width
        self.height = height
        self.resolution = resolution

        self.cols = width // resolution + 1
        self.rows = height // resolution + 1

        self.grid = np.zeros(
            (self.rows, self.cols),
            dtype=float
        )

        self.diffusion_rate = diffusion_rate
        self.decay_rate = decay_rate

    # -----------------------------------------

    def deposit(
        self,
        x,
        y,
        amount=1.0
    ):

        col = int(x / self.resolution)
        row = int(y / self.resolution)

        if (
            0 <= row < self.rows
            and
            0 <= col < self.cols
        ):

            self.grid[row, col] += amount

    # -----------------------------------------

    def diffuse(self):

        new_grid = self.grid.copy()

        for row in range(1, self.rows - 1):

            for col in range(1, self.cols - 1):

                neighbor_avg = (

                    self.grid[row-1, col] +

                    self.grid[row+1, col] +

                    self.grid[row, col-1] +

                    self.grid[row, col+1]

                ) / 4.0

                new_grid[row, col] += (

                    self.diffusion_rate
                    *
                    (
                        neighbor_avg
                        -
                        self.grid[row, col]
                    )

                )

        self.grid = new_grid

        self.grid *= 0.995

    # -----------------------------------------

    def decay(self):

        self.grid *= (

            1.0
            -
            self.decay_rate

        )

    # -----------------------------------------

    def update(self):

        self.diffuse()

        self.decay()

    # -----------------------------------------

    def cytokine_at(
        self,
        x,
        y
    ):

        col = int(x / self.resolution)
        row = int(y / self.resolution)

        row = max(
            0,
            min(row, self.rows - 1)
        )

        col = max(
            0,
            min(col, self.cols - 1)
        )

        return self.grid[row, col]