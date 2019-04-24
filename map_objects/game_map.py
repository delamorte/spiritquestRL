from entity import Entity
from map_objects.tile import Tile
from map_objects.tilemap import tilemap
from random import randint

class Room:
    def __init__(self, x, y, w, h, wall, wall_color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.wall = wall
        self.wall_color = wall_color
        
    def get_walls(self):

        walls = [()]

        for y in range(self.y, self.y+self.h):
            for x in range(self.x, self.x+self.w):
                if (x == self.x or x == self.w - 1 or
                        y == self.y or y == self.h - 1):
                    walls.append((x, y))
                    
        return walls

class GameMap:
    def __init__(self, width, height, name):
        self.width = width
        self.height = height
        self.name = name
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):

        tiles = [[Tile(False, False)
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
 
    def create_room(self, room):

        x2 = room.x + room.w
        y2 = room.y + room.h
        
        for y in range(room.y, y2):
            for x in range(room.x, x2):
                if (x == room.x or x == x2 - 1 or
                        y == room.y or y == y2 - 1):
                    self.tiles[x][y].color[1] = room.wall_color
                    self.tiles[x][y].char[1] = room.wall
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
                else:
                    self.tiles[x][y].color[0] = "dark gray"
                    self.tiles[x][y].char[0] = tilemap()["floor"]
                    self.tiles[x][y].char[1] = " "
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False
                    self.tiles[x][y].spawnable = True

    def generate_hub(self):

        self.generate_trees(0, 0, self.width, self.height,
                            20, block_sight=None)
        
        # Generate a house
        w = 10
        h = 10
        x1 = randint(1, self.width - w - 1)
        y1 = randint(1, self.height - h - 1)
        
        home = Room(x1, y1, w, h, tilemap()["wall_brick"], "orange")
        
        self.create_room(home)
        
        center_x = int((home.x + home.x + home.w) / 2)
        center_y = int((home.y + home.x + home.h) / 2)

        self.tiles[center_x][center_y].color[1] = "lightest orange"
        self.tiles[center_x][center_y].char[1] = tilemap()["campfire"]

        # Generate one door at a random position in the room.
        door_seed = randint(0, len(home.get_walls())-1)
        walls = home.get_walls()

        self.tiles[walls[door_seed][0]][walls[door_seed][1]].color[1] = None        
        self.tiles[walls[door_seed][0]][walls[door_seed][1]].char[1] = tilemap()[
            "door_closed"]
        self.tiles[walls[door_seed][0]][walls[door_seed][1]].blocked = True
        self.tiles[walls[door_seed][0]][walls[door_seed][1]].block_sight = False
        
        # Create starting weapon in hub
        #weapon = Entity(center_x)

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

        # Generate rocks & rubble on floor tiles
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.is_blocked(x, y):
                    if randint(1, 4) >= self.tiles[x][y].seed:
                        self.tiles[x][y].color[1] = "dark gray"
                        self.tiles[x][y].char[1] = tilemap()["rubble"][randint(
                            0, (len(tilemap()["rubble"]) - 1))]

    def generate_trees(self, dx, dy, width, height, freq, block_sight):
        """Generate a forest to a rectangular area."""

        forest_colors = ["lightest orange",
                         "lighter orange",
                         "light orange",
                         "dark orange",
                         "darker orange"]

        for y in range(dy, height):
            for x in range(dx, width):
                self.tiles[x][y].color[0] = "darkest amber"
                self.tiles[x][y].char[0] = tilemap()["ground_soil"]
                # Generate forest tiles
                if randint(0, 100) < freq:
                    self.tiles[x][y].char[1] = tilemap()["tree"][randint(
                        0, (len(tilemap()["tree"]) - 1))]
                    self.tiles[x][y].color[1] = forest_colors[randint(0, 4)]
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
            for x, y in tilemap()["monsters"].items():
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
                    monster = Entity(x, y, 12, char,
                                     None, name, blocks=True, fighter=True, ai=True)
                    entities.append(monster)

        return player, entities
