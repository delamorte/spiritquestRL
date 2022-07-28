import numpy as np
from tcod.map import compute_fov


class LightSource:
    def __init__(self, radius=3, name=None, fov_map=None, light_walls=False):
        self.owner = None
        self.radius = radius
        self.fov_map = fov_map
        self.algorithm = 0
        self.light_walls = light_walls
        self.name = name
        self.visible = None

    def initialize_fov(self, game_map):
        self.fov_map = np.full((game_map.width, game_map.height), fill_value=False)

    def recompute_fov(self, game_map):
        x, y = self.owner.x, self.owner.y

        # Update visible tiles
        self.fov_map[:] = compute_fov(
            game_map.transparent,
            (x, y),
            radius=self.radius
        )
