from map_objects.tile import Tile
from random import randint


class GameMap:
    def __init__(self, width, height, name):
        self.width = width
        self.height = height
        self.name = name
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

    def generate_hub(self):

        self.generate_forest(0, 0, self.width, self.height, 75)
        width = 10
        height = 10

        x1 = randint(1, self.width - width - 1)
        x2 = x1 + 10
        y1 = randint(1, self.height - height - 1)
        y2 = y1 + 10

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        for y in range(y1, y2):
            for x in range(x1, x2):
                if (x == x1 or x == x2 - 1 or
                        y == y1 or y == y2 - 1):
                    self.tiles[x][y].color = "orange"
                    self.tiles[x][y].char = 0xE100 + 83
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
                else:
                    self.tiles[x][y].color = "darkest amber"
                    self.tiles[x][y].char_ground = 0xE100 + 21
                    self.tiles[x][y].char = 0xE100 + 21
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False
                    self.tiles[x][y].spawnable = True
        self.tiles[center_x][center_y].color = "lightest orange"
        self.tiles[center_x][center_y].char = 0xE100 + 427

        # Generate one door at a random position in the room.
        # There has to be a simpler way of doing this....
        door_y = randint(y1, y2 - 1)
        door_x = randint(x1, x2 - 1)
        door_seed = randint(0, 3)

        if door_seed == 0:
            self.tiles[x1][door_y].color = None
            self.tiles[x1][door_y].char = 0xE100 + 67
            self.tiles[x1][door_y].blocked = True
            self.tiles[x1][door_y].block_sight = False
        if door_seed == 1:
            self.tiles[x2 - 1][door_y].color = None
            self.tiles[x2 - 1][door_y].char = 0xE100 + 67
            self.tiles[x2 - 1][door_y].blocked = True
            self.tiles[x2 - 1][door_y].block_sight = False
        if door_seed == 2:
            self.tiles[door_x][y1].color = None
            self.tiles[door_x][y1].char = 0xE100 + 67
            self.tiles[door_x][y1].blocked = True
            self.tiles[door_x][y1].block_sight = False
        if door_seed == 3:
            self.tiles[door_x][y2 - 1].color = None
            self.tiles[door_x][y2 - 1].char = 0xE100 + 67
            self.tiles[door_x][y2 - 1].blocked = True
            self.tiles[door_x][y2 - 1].block_sight = False

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
