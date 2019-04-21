from entity import Entity
from map_objects.tile import Tile
from map_objects.tilemap import tilemap
from random import randint


class GameMap:
    def __init__(self, width, height, name):
        self.width = width
        self.height = height
        self.name = name
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):

        tiles = [[Tile(False, False, randint(0, 100), " ", tilemap()["floor"])
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

        self.generate_trees(0, 0, self.width, self.height,
                            75, block_sight=None)
        width = 10
        height = 10

        x1 = randint(1, self.width - width - 1)
        x2 = x1 + 10
        y1 = randint(1, self.height - height - 1)
        y2 = y1 + 10

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        wall_x = []
        wall_y = []

        for y in range(y1, y2):
            for x in range(x1, x2):
                if (x == x1 or x == x2 - 1 or
                        y == y1 or y == y2 - 1):
                    self.tiles[x][y].color = "orange"
                    self.tiles[x][y].char = tilemap()["wall_brick"]
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
                    wall_x.append(x)
                    wall_y.append(y)
                else:
                    self.tiles[x][y].color = "darkest amber"
                    self.tiles[x][y].char_ground = tilemap()["floor"]
                    self.tiles[x][y].char = tilemap()["floor"]
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False
                    self.tiles[x][y].spawnable = True
        self.tiles[center_x][center_y].color = "lightest orange"
        self.tiles[center_x][center_y].char = tilemap()["campfire"]

        # Generate one door at a random position in the room.
        door_seed = randint(0, len(wall_x) - 1)
        self.tiles[wall_x[door_seed]][wall_y[door_seed]].color = None
        self.tiles[wall_x[door_seed]][wall_y[door_seed]].char = tilemap()["door_closed"]
        self.tiles[wall_x[door_seed]][wall_y[door_seed]].blocked = True
        self.tiles[wall_x[door_seed]][wall_y[door_seed]].block_sight = False

    def generate_forest(self):

        for i in range(self.width):
            dx = randint(1, self.width - 1)
            dy = randint(1, self.height - 1)
            width = dx + randint(5, self.width / 5)
            if width > self.width:
                width = self.width
            height = dy + randint(5, self.width / 5)
            if height > self.height:
                height = self.height
            freq = randint(10, 40)
            block_sight = True
            self.generate_trees(dx, dy, width, height, freq, block_sight)

    def generate_trees(self, dx, dy, width, height, freq, block_sight):
        """Generate a forest to a rectangular area."""

        forest_colors = ["lightest orange",
                         "lighter orange",
                         "light orange",
                         "dark orange",
                         "darker orange"]

        for y in range(dy, height):
            for x in range(dx, width):
                self.tiles[x][y].char_ground = tilemap()["ground_soil"]
                # Generate forest tiles
                if randint(0, 100) < freq:
                    self.tiles[x][y].char = tilemap()["tree"][randint(0,(len(tilemap()["tree"])-1))]
                    self.tiles[x][y].color = forest_colors[randint(0, 4)]
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = block_sight

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, player):

        # Initialize player, starting position and other entities
        px, py = randint(1, self.width - 1), \
            randint(1, self.height - 1)

        while self.is_blocked(px, py):
            px, py = randint(1, self.width - 1), \
                randint(1, self.height - 1)
        player.x = px
        player.y = py

        if self.name == "hub":
            for x in range(self.width - 1):
                for y in range(self.height - 1):
                    if self.tiles[x][y].spawnable:
                        player.x = x - 1
                        player.y = y - 1

        # if self.name == "debug":
        #    player.x, player.y = 2, 2

        entities = [player]

        if self.name is "dream":

            number_of_monsters = randint(self.width / 2 - 20, self.width / 2)
            monsters = []
            for x,y in tilemap()["monsters"].items():
                monsters.append((x, y))

            for i in range(number_of_monsters):
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y):
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)

                if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                    r = randint(0, 2)
                    name, char = monsters[r]
                    monster = Entity(x, y, 50, char,
                                     None, name, blocks=True, fighter=True, ai=True)
                    entities.append(monster)

        return player, entities
