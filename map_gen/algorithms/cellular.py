import random

from map_gen.dungeon import Dungeon, Room


# ==== Cellular Automata ====
class CellularAutomata(Dungeon):
    '''
    Rather than implement a traditional cellular automata, I
    decided to try my hand at a method discribed by "Evil
    Scientist" Andy Stobirski that I recently learned about
    on the Grid Sage Games blog.
    '''

    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.rooms = []

        self.iterations = 10000
        self.neighbors = 3  # number of neighboring walls for this cell to become a wall

        # the initial probability of a cell becoming a wall,
        # recommended to be between .35 and .55
        self.wall_probability = 0.45

        self.ROOM_MIN_SIZE = 16  # size in total number of cells, not dimensions
        self.ROOM_MAX_SIZE = 500  # size in total number of cells, not dimensions

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
        self.connect_caves()
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

    def create_tunnel(self, point1, point2, current_cave):
        # run a heavily weighted random Walk
        # from point1 to point1
        drunkard_x = point2[0]
        drunkard_y = point2[1]
        while (drunkard_x, drunkard_y) not in current_cave:
            # ==== Choose Direction ====
            north = 1.0
            south = 1.0
            east = 1.0
            west = 1.0

            weight = 1

            # weight the random walk against edges
            if drunkard_x < point1[0]:  # drunkard is left of point1
                east += weight
            elif drunkard_x > point1[0]:  # drunkard is right of point1
                west += weight
            if drunkard_y < point1[1]:  # drunkard is above point1
                south += weight
            elif drunkard_y > point1[1]:  # drunkard is below point1
                north += weight

            # normalize probabilities so they form a range from 0 to 1
            total = north + south + east + west
            north /= total
            south /= total
            east /= total
            west /= total

            # choose the direction
            choice = random.random()
            if 0 <= choice < north:
                dx = 0
                dy = -1
            elif north <= choice < (north + south):
                dx = 0
                dy = 1
            elif (north + south) <= choice < (north + south + east):
                dx = 1
                dy = 0
            else:
                dx = -1
                dy = 0

            # ==== Walk ====
            # check collision at edges
            if (0 < drunkard_x + dx < self.map_width - 1) and (0 < drunkard_y + dy < self.map_height - 1):
                drunkard_x += dx
                drunkard_y += dy
                if self.level[drunkard_x][drunkard_y] == 1:
                    self.level[drunkard_x][drunkard_y] = 0

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

    def flood_fill(self, x, y):
        '''
        flood fill the separate regions of the level, discard
        the regions that are smaller than a minimum size, and
        create a reference for the rest.
        '''
        cave = set()
        tile = (x, y)
        to_be_filled = {tile}
        while to_be_filled:
            tile = to_be_filled.pop()

            if tile not in cave:
                cave.add(tile)

                self.level[tile[0]][tile[1]] = 1

                # check adjacent cells
                x = tile[0]
                y = tile[1]
                north = (x, y - 1)
                south = (x, y + 1)
                east = (x + 1, y)
                west = (x - 1, y)

                for direction in [north, south, east, west]:

                    if self.level[direction[0]][direction[1]] == 0:
                        if direction not in to_be_filled and direction not in cave:
                            to_be_filled.add(direction)

        if self.ROOM_MIN_SIZE <= len(cave) <= self.ROOM_MAX_SIZE:

            x1 = min(cave, key=lambda t: t[0])[0]
            x2 = max(cave, key=lambda t: t[0])[0]
            y1 = min(cave, key=lambda t: t[1])[1]
            y2 = max(cave, key=lambda t: t[1])[1]
            w = x2 - x1
            h = y2 - y1
            id_nr = len(self.rooms) + 1

            room = Room(x1=x1, y1=y1, x2=x2, y2=y2, w=w, h=h, cave=cave, id_nr=id_nr)
            self.rooms.append(room)

    def connect_caves(self):
        # Find the closest cave to the current cave
        for current_cave_room in self.rooms:
            current_cave = current_cave_room.cave
            for point1 in current_cave:
                break  # get an element from cave1
            point2 = None
            distance = None
            for next_cave_room in self.rooms:
                next_cave = next_cave_room.cave
                if next_cave != current_cave and not self.check_connectivity(current_cave, next_cave):
                    # choose a random point from next_cave
                    for next_point in next_cave:
                        break  # get an element from cave1
                    # compare distance of point1 to old and new point2
                    new_distance = self.distance_formula(point1, next_point)
                    if new_distance is not None and distance is not None and (
                            new_distance < distance) or distance is None:
                        point2 = next_point
                        distance = new_distance

            if point2:  # if all tunnels are connected, point2 == None
                self.create_tunnel(point1, point2, current_cave)

    def check_connectivity(self, cave1, cave2):
        # floods cave1, then checks a point in cave2 for the flood

        connected_region = set()
        for start in cave1:
            break  # get an element from cave1

        to_be_filled = {start}
        while to_be_filled:
            tile = to_be_filled.pop()

            if tile not in connected_region:
                connected_region.add(tile)

                # check adjacent cells
                x = tile[0]
                y = tile[1]
                north = (x, y - 1)
                south = (x, y + 1)
                east = (x + 1, y)
                west = (x - 1, y)

                for direction in [north, south, east, west]:

                    if self.level[direction[0]][direction[1]] == 0:
                        if direction not in to_be_filled and direction not in connected_region:
                            to_be_filled.add(direction)

        for end in cave2:
            break  # get an element from cave2

        if end in connected_region:
            return True

        else:
            return False
