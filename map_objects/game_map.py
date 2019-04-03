from map_objects.tile import Tile
from random import randint


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):

        tiles = [[Tile(False, False, randint(0, 100))
                  for y in range(self.height)]
                 for x in range(self.width)]

        # Block edges of map
        for y in range(self.height):
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or
                        y == 0 or y == self.height - 1):
                    tiles[x][y].blocked = True
                    tiles[x][y].block_sight = True

        return tiles

    def generate_forest(self, dx, dy, width, height, freq):
        """Generate a forest to a rectangular area."""

        forest_tiles = [87, 88, 89, 93, 94, 95]
        forest_colors = ["lightest orange",
                         "lighter orange",
                         "light orange",
                         "dark orange",
                         "darker orange",
                         "darkest orange"]
        ground_tiles = [21]

        for y in range(dy, height):
            for x in range(dx, width):
                self.tiles[x][y].char_ground = 0xE100 + ground_tiles[0]
                # Generate forest tiles
                if randint(0, 100) < freq:
                    self.tiles[x][y].char = 0xE100 + \
                        forest_tiles[randint(0, 5)]
                    self.tiles[x][y].color = forest_colors[randint(0, 5)]
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
