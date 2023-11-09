import random

from map_gen.dungeon import Dungeon


# ==== Cellular Automata ====
class CellularAutomata(Dungeon):
    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.rooms = []

        self.iterations = 10000
        self.neighbors = 3  # number of neighboring walls for this cell to become a wall

        # the initial probability of a cell becoming a wall,
        # recommended to be between .35 and .55
        self.wall_probability = 0.45

        self.room_min_size = 16  # size in total number of cells, not dimensions
        self.room_max_size = 500  # size in total number of cells, not dimensions

        self.smoothing = 1
        self.clean_up_iterations = 5
        self.name = "CellularAutomata"

    def generate_level(self):
        # Creates an empty 2D array or clears existing array
        self.level = [[1
                       for y in range(self.map_height)]
                      for x in range(self.map_width)]

        self.random_fill_map()
        self.create_caves()
        self.get_caves()
        self.connect_caves_old()
        self.clean_up_map(self.map_width, self.map_height)
        self.adjacent_rooms_path_scan(max_length=20)
        return self.level

    def random_fill_map(self):
        for y in range(1, self.map_height - 1):
            for x in range(1, self.map_width - 1):
                if random.random() >= self.wall_probability:
                    self.level[x][y] = 0

    def create_caves(self):
        # ==== Create distinct caves ====
        for i in range(0, self.iterations):
            # Pick a random point with a buffer around the edges of the map
            tile_x = random.randint(1, self.map_width - 2)
            tile_y = random.randint(1, self.map_height - 2)

            adjacent_walls = self.get_adjacent_walls(tile_x, tile_y)

            # if the cell's neighboring walls > self.neighbors, set it to 1
            if adjacent_walls > self.neighbors:
                self.level[tile_x][tile_y] = 1
            # or set it to 0
            elif adjacent_walls < self.neighbors:
                self.level[tile_x][tile_y] = 0

        # ==== Clean Up Map ====
        self.clean_up_map(self.map_width, self.map_height, smoothing=self.smoothing, iterations=self.clean_up_iterations)

    def get_caves(self):
        # locate all the caves within self.level and store them in self.rooms
        for x in range(0, self.map_width):
            for y in range(0, self.map_height):
                if self.level[x][y] == 0:
                    self.flood_fill(x, y)

        for room in self.rooms:
            cave = room.cave
            for tile in cave:
                self.level[tile[0]][tile[1]] = 0
