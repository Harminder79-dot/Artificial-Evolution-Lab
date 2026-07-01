class Camera:

    def __init__(self):

        self.x = 0
        self.y = 0

        self.zoom = 2.0

        self.target_x = 0
        self.target_y = 0


    def update(self):

        self.x += (self.target_x - self.x) * 0.08
        self.y += (self.target_y - self.y) * 0.08


    def world_to_screen(self, x, y):

        sx = (x - self.x) * self.zoom
        sy = (y - self.y) * self.zoom

        return sx, sy


    def screen_to_world(self, x, y):

        wx = x / self.zoom + self.x
        wy = y / self.zoom + self.y

        return wx, wy
    
    def move(self, dx, dy):

        self.target_x += dx / self.zoom
        self.target_y += dy / self.zoom


    def zoom_in(self):

        self.zoom = min(4.0, self.zoom * 1.1)


    def zoom_out(self):

        self.zoom = max(0.3, self.zoom / 1.1)

    def reset(self):

        self.x = 0
        self.y = 0

        self.target_x = 0
        self.target_y = 0

        self.zoom = 1.0