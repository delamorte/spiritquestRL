import random

import numpy as np
from scipy.ndimage import label
from scipy.signal import convolve2d

import options
from map_gen.dungeon import Dungeon, Room


# ==== Room Addition ====
class RoomAddition(Dungeon):
    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.rooms = []
        self.rooms_list = []
        self.level = []

        self.room_min_size = 16  # min size in number of floor tiles, not height and width
        self.room_max_size = 300  # min size in number of floor tiles, not height and width
        self.max_rooms = 20

        self.build_room_attempts = 400
        self.place_room_attempts = 10
        self.max_tunnel_length = 20

        self.cellular_room_max_size = 18  # max height and width for cellular automata rooms

        self.square_room_max_size = 12
        self.square_room_min_size = 6

        self.cross_room_max_size = 14
        self.cross_room_min_size = 4

        self.cavern_chance = 0.30  # probability that the first room will be a cavern
        self.cavern_max_size = 16  # max height an width

        self.conjoined_room_chance = 0.0  # chance to make room conjoined with other rooms

        self.vault_max_size = 1200

        self.wall_probability = 0.45
        self.neighbors = 4

        self.square_room_chance = 0.1
        self.cross_room_chance = 0.15
        self.vault_chance = 0.4

        self.name = "RoomAddition"

    def generate_level(self):

        self.level = np.ones((self.map_height, self.map_width), dtype=int)

        for r in range(self.build_room_attempts):
            room_arr, vault = self.generate_room()

            room_height, room_width = room_arr.shape
            if room_height >= self.map_height - 1 or room_width >= self.map_width - 1:
                continue
            x = random.randint(1, self.map_width - room_width - 1)
            y = random.randint(1, self.map_height - room_height - 1)
            id_nr = len(self.rooms) + 1
            new_room = Room(x, y, room_width, room_height, room_arr, id_nr=id_nr)

            # Discard too small or too large rooms
            if len(new_room.inner) > self.room_max_size or len(new_room.inner) < self.room_min_size:
                continue

            conjoined_rooms = False
            choice = random.random()
            if choice < self.conjoined_room_chance:
                conjoined_rooms = True

            # Run through the other rooms and see if they intersect with this one.
            if any(new_room.intersects(other_room, inner=conjoined_rooms) for other_room in self.rooms):
                continue  # This room intersects, so go to the next attempt.
            # If there are no intersections then the room is valid.

            self.add_room(new_room)

            # A vault is a prefab which may consist of multiple rooms, use flood fill to add inner rooms
            if vault:
                rooms = self.get_rooms_by_flood_fill(new_room)
                if rooms:
                    for room in rooms:
                        self.add_room(room)
                        # Connect rooms

            if len(self.rooms) > self.max_rooms:
                break

        # self.get_caves()
        self.connect_caves_old()
        # self.connect_caves()
        # self.clean_up_map(self.map_width, self.map_height)
        # Connect rooms
        # self.connect_rooms()
        self.adjacent_rooms_scan()

        return self.level

    def generate_level_old(self):

        # self.level = [[1
        #                for y in range(self.map_height)]
        #               for x in range(self.map_width)]

        self.level = np.ones((self.map_height, self.map_width), dtype=int)

        # generate the first room
        room, room_x, room_y = None, None, None
        room_width, room_height = self.map_width, self.map_height
        while room_width >= self.map_width or room_height >= self.map_height and room_x > 1 and room_y > 1:
            room = self.generate_room()
            room_height, room_width = self.get_room_dimensions(room)

        self.add_room(room_x, room_y, room)

        # generate other rooms
        for i in range(self.build_room_attempts):
            room = self.generate_room()
            # try to position the room, get room_x and room_y
            room_x, room_y, wall_tile, direction, tunnel_length = self.place_room(room, self.map_width, self.map_height)
            if room_x and room_y:
                print(room_x, room_y)
                self.add_room(room_x, room_y, room)
                if len(self.rooms_list) >= self.MAX_NUM_ROOMS:
                    break

        self.get_caves()
        self.connect_caves_old()
        self.clean_up_map(self.map_width, self.map_height)
        self.adjacent_rooms_scan()

        return self.level

    def generate_room(self):
        vault = False
        # select a room type to generate and return that room
        if self.rooms:
            # There is at least one room already
            choice = random.random()

            if choice < self.vault_chance:
                room = self.generate_random_vault()
                vault = True

            else:
                if choice < self.square_room_chance:
                    room = self.generate_room_square()
                elif self.square_room_chance <= choice < (self.square_room_chance + self.cross_room_chance):
                    room = self.generate_room_cross()
                else:
                    room = self.generate_room_cellular()

        else:  # it's the first room
            choice = random.random()
            if choice < self.vault_chance:
                room = self.generate_random_vault()
                vault = True

            else:
                if choice < self.cavern_chance:
                    room = self.generate_room_cellular()
                else:
                    room = self.generate_room_square()

        return room, vault

    def generate_room_cross(self):
        room_hor_width = int((random.randint(self.cross_room_min_size + 2, self.cross_room_max_size)) / 2 * 2)
        room_ver_height = int((random.randint(self.cross_room_min_size + 2, self.cross_room_max_size)) / 2 * 3)
        room_hor_height = int((random.randint(self.cross_room_min_size, room_ver_height - 2)) / 2 * 2)
        room_ver_width = int((random.randint(self.cross_room_min_size, room_hor_width - 2)) / 2 * 1)

        # room = [[1
        #          for y in range(int(room_ver_height))]
        #         for x in range(int(room_hor_width))]
        room = np.ones((room_ver_height, room_hor_width), dtype=int)

        ver_offset = int(room_ver_height / 2 - room_hor_height / 2)
        hor_offset = int(room_hor_width / 2 - room_ver_width / 2)

        # Fill in vertical space
        room[ver_offset:room_hor_height + ver_offset, 0:room_hor_width] = 0
        room[0:room_ver_height, hor_offset:room_ver_width + hor_offset] = 0

        # for y in range(ver_offset, room_hor_height + ver_offset):
        #     for x in range(0, int(room_hor_width)):
        #         room[x][y] = 0
        #
        # # Fill in horizontal space
        # for y in range(0, room_ver_height):
        #     for x in range(hor_offset, room_ver_width + hor_offset):
        #         room[x][y] = 0

        return room

    def generate_random_vault(self):
        '''
        Parse vaults from Zorbus format into rooms
        Vault prefabs kindly provided by joonas@zorbus.net under the CC0 Creative Commons License:
        http://dungeon.zorbus.net/
        '''

        if options.data.vault_thread:
            options.data.vault_thread.join()
        room = random.choice([x for x in options.data.vaults_data if x.size < self.vault_max_size])

        return room

    def generate_room_square(self, padding=1):
        room_width = random.randint(self.square_room_min_size, self.square_room_max_size)
        room_height = random.randint(max(int(room_width * 0.5), self.square_room_min_size),
                                     min(int(room_width * 1.5), self.square_room_max_size))

        # room = [[0
        #          for y in range(1, room_height - 1)]
        #         for x in range(1, room_width - 1)]
        room = np.zeros((room_height, room_width), dtype=int)
        # If padding > 0, pad the room with walls
        if padding > 0:
            padded_room = np.pad(room, 1, constant_values=1)
        else:
            padded_room = room

        return padded_room

    def get_rooms_by_flood_fill(self, vault_room):

        rooms = []
        room_arr = vault_room.nd_array

        # Use scipy.ndimage.label to label all separated clusters (rooms) in an array
        col, row = np.where(room_arr == 0)
        y, x = col[0], row[0]
        labeled_rooms, num_of_rooms = label(room_arr == room_arr[y, x])

        # No rooms found
        if num_of_rooms <= 1:
            return rooms

        # Get the largest cluster/room
        largest_i = np.argmax(np.unique(labeled_rooms, return_counts=True)[1][1:]) + 1

        for i in range(1, num_of_rooms + 1):
            if i == largest_i:
                continue
            room = np.where(labeled_rooms == i, 0, 1)
            floors = np.where(room == 0)
            trimmed_room = room[floors[0].min():floors[0].max() + 1,
                           floors[1].min():floors[1].max() + 1]
            padded_room = np.pad(trimmed_room, 1, constant_values=1)
            id_nr = len(self.rooms) + 1
            room_height, room_width = padded_room.shape
            new_room = Room(vault_room.x1 + padded_room[1][0], vault_room.y1 + padded_room[0][0], room_width,
                            room_height, padded_room, id_nr=id_nr)
            rooms.append(new_room)

        return rooms

    def floodfill_by_xy_scipy(self, room, padding=1):

        # Use scipy.ndimage.label to label all separated clusters (rooms) in an array
        col, row = np.where(room == 0)
        y, x = col[0], row[0]
        labeled_rooms = label(room == room[y, x])[0]

        # Get the largest cluster/room
        i = np.argmax(np.unique(labeled_rooms, return_counts=True)[1][1:]) + 1
        largest_room = np.where(labeled_rooms == i, 0, 1)

        # Slice extra walls around the room (all rows & cols where all values == 1)
        floors = np.where(largest_room == 0)
        trimmed_room = largest_room[floors[0].min():floors[0].max() + 1,
                       floors[1].min():floors[1].max() + 1]

        # If padding > 0, pad the room with walls
        if padding > 0:
            padded_room = np.pad(trimmed_room, 1, constant_values=1)
        else:
            padded_room = trimmed_room

        return padded_room

    def generate_room_cellular(self, wall_rule=5):
        """Return the next step of the cave generation algorithm.

        `tiles` is the input array. (0: wall, 1: floor)

        If the 3x3 area around a tile (including itself) has `wall_rule` number of
        walls then the tile will become a wall.
        """
        convolve_steps = 4
        rng = np.random.default_rng()
        arr = rng.choice(2, (self.cellular_room_max_size - 1, self.cellular_room_max_size - 1), p=[1 - self.wall_probability, self.wall_probability])
        room = np.pad(arr, 1, constant_values=1)

        for _ in range(convolve_steps):
            neighbors = convolve2d(room == 0, [[1, 1, 1], [1, 1, 1], [1, 1, 1]], "same")
            room = np.where(neighbors < wall_rule, 0, 1)  # Apply the wall rule.
            room[[0, -1], :] = 1  # Ensure surrounding wall.
            room[:, [0, -1]] = 1

        # Remove isolated cells with flood fill
        room = self.floodfill_by_xy_scipy(room)

        return room

    def generate_room_cavern2(self, max_size=18):
        while True:
            # if a room is too small, generate another
            room = [[1
                     for y in range(max_size)]
                    for x in range(max_size)]

            # random fill map
            for y in range(2, max_size - 2):
                for x in range(2, max_size - 2):
                    if random.random() >= self.wall_probability:
                        room[x][y] = 0

            # create distinctive regions
            for i in range(4):
                for y in range(1, max_size - 1):
                    for x in range(1, max_size - 1):

                        # if the cell's neighboring walls > self.neighbors, set it to 1
                        if self.get_adjacent_walls(x, y, room) > self.neighbors:
                            room[x][y] = 1
                        # otherwise, set it to 0
                        elif self.get_adjacent_walls(x, y, room) < self.neighbors:
                            room[x][y] = 0

            # flood_fill to remove small caverns
            room = self.flood_fill_remove(room)

            # start over if the room is completely filled in
            room_height, room_width = self.get_room_dimensions(room)
            for x in range(room_width):
                for y in range(room_height):
                    if room[x][y] == 0:
                        return room

    def flood_fill_remove(self, room):
        '''
        Find the largest region. Fill in all other regions.
        '''
        room_height, room_width = self.get_room_dimensions(room)
        largestRegion = set()

        for x in range(room_width):
            for y in range(room_height):
                if room[x][y] == 0:
                    newRegion = set()
                    tile = (x, y)
                    to_be_filled = set([tile])
                    while to_be_filled:
                        tile = to_be_filled.pop()

                        if tile not in newRegion:
                            newRegion.add(tile)

                            room[tile[0]][tile[1]] = 1

                            # check adjacent cells
                            x = tile[0]
                            y = tile[1]
                            north = (x, y - 1)
                            south = (x, y + 1)
                            east = (x + 1, y)
                            west = (x - 1, y)

                            for direction in [north, south, east, west]:

                                if room[direction[0]][direction[1]] == 0:
                                    if direction not in to_be_filled and direction not in newRegion:
                                        to_be_filled.add(direction)

                    if len(newRegion) >= self.room_min_size:
                        if len(newRegion) > len(largestRegion):
                            largestRegion.clear()
                            largestRegion.update(newRegion)

        for tile in largestRegion:
            room[tile[0]][tile[1]] = 0

        return room

    def place_room(self, room, map_width, map_height):  # (self,room,direction,)

        room_height, room_width = self.get_room_dimensions(room)
        if room_width >= map_width or room_height >= map_height:
            return None, None, None, None, None

        # try n times to find a wall that lets you build room in that direction
        for i in range(self.place_room_attempts):
            # try to place the room against the tile, else connected by a tunnel of length i

            wall_tile = None
            direction = self.get_direction()
            while not wall_tile:
                '''
                randomly select tiles until you find
                a wall that has another wall in the
                chosen direction and has a floor in the 
                opposite direction.
                '''
                # direction == tuple(dx,dy)
                tile_x = random.randint(2, map_width - 2)
                tile_y = random.randint(2, map_height - 2)
                if ((self.level[tile_x][tile_y] == 1) and
                        (self.level[tile_x + direction[0]][tile_y + direction[1]] == 1) and
                        (self.level[tile_x - direction[0]][tile_y - direction[1]] == 0)):
                    wall_tile = (tile_x, tile_y)

            # spawn the room touching wall_tile
            start_room_x = None
            start_room_y = None
            '''
            TODO: replace this with a method that returns a 
            random floor tile instead of the top left floor tile
            '''
            while not start_room_x and not start_room_y:
                x = random.randint(0, room_width - 1)
                y = random.randint(0, room_height - 1)
                if room[x][y] == 0:
                    start_room_x = wall_tile[0] - x
                    start_room_y = wall_tile[1] - y

            # then slide it until it doesn't touch anything
            for tunnel_length in range(self.max_tunnel_length):
                possible_room_x = start_room_x + direction[0] * tunnel_length
                possible_room_y = start_room_y + direction[1] * tunnel_length

                enough_room = self.get_overlap(room, possible_room_x, possible_room_y, map_width, map_height)

                if enough_room:
                    room_x = possible_room_x
                    room_y = possible_room_y
                    # build connecting tunnel
                    # Attempt 1
                    '''
                    for i in range(tunnel_length+1):
                        x = wall_tile[0] + direction[0]*i
                        y = wall_tile[1] + direction[1]*i
                        self.level[x][y] = 0
                    '''
                    # moved tunnel code into self.generate_level()
                    return room_x, room_y, wall_tile, direction, tunnel_length

        return None, None, None, None, None

    def add_room(self, room):

        self.level[room.y1:room.y1 + room.h, room.x1:room.x1 + room.w] = room.nd_array
        self.rooms.append(room)

    def get_direction(self):
        # direction = (dx,dy)
        north = (0, -1)
        south = (0, 1)
        east = (1, 0)
        west = (-1, 0)

        direction = random.choice([north, south, east, west])
        return direction

    def get_overlap(self, room, roomX, roomY, map_width, map_height):
        '''
        for each 0 in room, check the cooresponding tile in
        self.level and the eight tiles around it. Though slow,
        that should insure that there is a wall between each of
        the rooms created in this way.
        <> check for overlap with self.level
        <> check for out of bounds
        '''
        room_width, room_height = self.get_room_dimensions(room)
        for x in range(room_width):
            for y in range(room_height):
                if room[x][y] == 0:
                    # Check to see if the room is out of bounds
                    if ((3 <= (x + 1 + roomX) < map_width - 1) and
                            (3 <= (y + 1 + roomY) < map_height - 1)):
                        # Check for overlap with a one tile buffer
                        if self.level[x + roomX - 1][y + roomY - 1] == 0 or self.level[x + roomX - 2][
                            y + roomY - 2] == 0:  # top left
                            return False
                        if self.level[x + roomX][y + roomY - 1] == 0 or self.level[x + roomX][
                            y + roomY - 2] == 0:  # top center
                            return False
                        if self.level[x + roomX + 1][y + roomY - 1] == 0 or self.level[x + roomX + 2][
                            y + roomY - 2] == 0:  # top right
                            return False

                        if self.level[x + roomX - 1][y + roomY] == 0 or self.level[x + roomX - 2][
                            y + roomY] == 0:  # left
                            return False
                        if self.level[x + roomX][y + roomY] == 0:  # center
                            return False
                        if self.level[x + roomX + 1][y + roomY] == 0 or self.level[x + roomX + 2][
                            y + roomY] == 0:  # right
                            return False

                        if self.level[x + roomX - 1][y + roomY + 1] == 0 or self.level[x + roomX - 2][
                            y + roomY + 2] == 0:  # bottom left
                            return False
                        if self.level[x + roomX][y + roomY + 1] == 0 or self.level[x + roomX][
                            y + roomY + 2] == 0:  # bottom center
                            return False
                        if self.level[x + roomX + 1][y + roomY + 1] == 0 or self.level[x + roomX + 2][
                            y + roomY + 2] == 0:  # bottom right
                            return False

                    else:  # room is out of bounds
                        return False
        return True
