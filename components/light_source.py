from tcod import map


class LightSource:
    def __init__(self, radius=3, name=None, fov_map=None):
        self.owner = None
        self.radius = radius
        self.fov_map = fov_map
        self.algorithm = 0
        self.light_walls = True
        self.name = name
        if self.name == "candle":
            self.radius = 0

    def initialize_fov(self, game_map):
        fov_map = map.Map(game_map.width, game_map.height)
        fov_map.walkable[:] = True
        fov_map.transparent[:] = True

        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.tiles[x][y].blocked:
                    fov_map.walkable[y, x] = False
                if game_map.tiles[x][y].block_sight:
                    fov_map.transparent[y, x] = False

        self.fov_map = fov_map

    def recompute_fov(self, x, y):
        self.fov_map.compute_fov(x, y, self.radius, self.light_walls, self.algorithm)
