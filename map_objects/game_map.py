from map_objects.tile import Tile
from random import randint


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):

        tiles = [[Tile(False, False, x, y, randint(0, 100), False) for y in range(self.height)]
                 for x in range(self.width)]

        return tiles

    def generate_forest(self, map):

        for y in range(self.height):
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or
                        y == 0 or y == self.height - 1):
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
                # Spawn forest seeds
                elif randint(0, 100) < 25:
                    self.tiles[x][y].forest = True
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
