import random

import numpy as np
from scipy.ndimage import label
from scipy.signal import convolve2d

import options
from map_gen.algorithms.drunkards import DrunkardsWalk
from map_gen.dungeon import Dungeon, Room


# ==== Room Addition ====
class RoomAddition(Dungeon):
    def __init__(self, map_width=None, map_height=None, only_cellular=False, only_vaults=False,
                 only_squares=False, squares_and_crosses=False, drunkard=False, max_rooms=20, room_max_size=300):
        super().__init__(map_width=map_width, map_height=map_height)
        self.rooms = []
        self.rooms_list = []
        self.level = []

        self.room_min_size = 16  # min size in number of floor tiles, not height and width
        self.room_max_size = room_max_size  # min size in number of floor tiles, not height and width
        self.max_rooms = max_rooms

        self.build_room_attempts = 500
        self.place_room_attempts = 10
        self.max_tunnel_length = 20

        self.square_room_max_size = 12
        self.square_room_min_size = 6

        self.cross_room_max_size = 14
        self.cross_room_min_size = 4

        self.cellular_chance = 0.30  # probability that the first room will be a cavern
        self.cellular_room_min_size = 6  # max height and width for cellular automata rooms
        self.cellular_room_max_size = 14  # max height and width for cellular automata rooms

        self.conjoined_room_chance = 0.0  # chance to make room conjoined with other rooms

        self.first_vault_max_size = 1600
        self.vault_max_size = 1100
        self.vault_size_offset = 200  # After enough rooms are placed, fetch smaller vaults

        self.cellular_wall_probability = 0.45
        self.cellular_neighbors = 5
        self.cellular_iterations = 4

        self.square_room_chance = 0.1
        self.cross_room_chance = 0.15
        self.vault_chance = 0.2

        self.only_cellular = only_cellular
        self.only_vaults = only_vaults
        self.only_squares = only_squares
        self.squares_and_crosses = squares_and_crosses
        self.drunkard = drunkard

        self.name = "RoomAddition"

    def generate_level(self):

        if self.drunkard:
            self.level = DrunkardsWalk(self.map_width, self.map_height).generate_level()
        else:
            self.level = np.ones((self.map_height, self.map_width), dtype=np.int32)
        vault_size_offset = 0
        for r in range(self.build_room_attempts):
            if r == 0:
                vault_size_offset = self.first_vault_max_size
            elif len(self.rooms) > 4:
                vault_size_offset = self.vault_size_offset
            room_arr, algorithm = self.generate_room(vault_size_offset)

            room_height, room_width = room_arr.shape
            if room_height >= self.map_height - 1 or room_width >= self.map_width - 1:
                continue
            x = random.randint(1, self.map_width - room_width - 1)
            y = random.randint(1, self.map_height - room_height - 1)
            id_nr = len(self.rooms) + 1
            new_room = Room(x, y, room_width, room_height, room_arr, id_nr=id_nr, algorithm=algorithm)

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
            if algorithm == "vault":
                rooms = self.get_rooms_by_flood_fill(new_room)
                if rooms:
                    for room in rooms:
                        self.add_room(room)
                        # Connect rooms

            if len(self.rooms) >= self.max_rooms:
                break

        self.connect_caves()
        # self.adjacent_rooms_scan()

        return self.level

    def generate_room(self, vault_size_offset=0):
        algorithm = None
        # select a room type to generate and return that room
        if self.only_cellular:
            self.conjoined_room_chance = 1.0
            room = self.generate_room_cellular()
            return room, "cellular"
        if self.only_vaults:
            vault_size = self.vault_max_size - vault_size_offset
            room = self.generate_random_vault(vault_size)
            return room, "vault"
        if self.only_squares:
            room = self.generate_room_square()
            return room, "square"
        if self.squares_and_crosses:
            choice = random.random()
            if choice < self.vault_chance:
                room = self.generate_room_square()
                algorithm = "square"
            else:
                room = self.generate_room_cross()
                algorithm = "cross"
            return room, algorithm
        if self.rooms:
            # There is at least one room already
            choice = random.random()

            if choice < self.vault_chance:
                vault_size = self.vault_max_size - vault_size_offset
                room = self.generate_random_vault(vault_size)
                algorithm = "vault"

            else:
                if choice < self.square_room_chance:
                    room = self.generate_room_square()
                    algorithm = "square"
                elif self.square_room_chance <= choice < (self.square_room_chance + self.cross_room_chance):
                    room = self.generate_room_cross()
                    algorithm = "cross"
                else:
                    room = self.generate_room_cellular()
                    algorithm = "cellular"

        else:  # it's the first room
            choice = random.random()
            if choice < self.vault_chance:
                room = self.generate_random_vault(self.first_vault_max_size)
                algorithm = "vault"

            else:
                if choice < self.cellular_chance:
                    room = self.generate_room_cellular()
                    algorithm = "cellular"
                else:
                    room = self.generate_room_square()
                    algorithm = "square"

        return room, algorithm

    def generate_room_cross(self):
        room_hor_width = int((random.randint(self.cross_room_min_size + 2, self.cross_room_max_size)) / 2 * 2)
        room_ver_height = int((random.randint(self.cross_room_min_size + 2, self.cross_room_max_size)) / 2 * 3)
        room_hor_height = int((random.randint(self.cross_room_min_size, room_ver_height - 2)) / 2 * 2)
        room_ver_width = int((random.randint(self.cross_room_min_size, room_hor_width - 2)) / 2 * 1)

        room = np.ones((room_ver_height, room_hor_width), dtype=np.int32)

        ver_offset = int(room_ver_height / 2 - room_hor_height / 2)
        hor_offset = int(room_hor_width / 2 - room_ver_width / 2)

        # Fill in vertical space
        room[ver_offset:room_hor_height + ver_offset, 0:room_hor_width] = 0
        room[0:room_ver_height, hor_offset:room_ver_width + hor_offset] = 0

        return room

    def generate_random_vault(self, max_size=None):
        if not max_size:
            max_size = self.vault_max_size
        if options.data.vault_thread:
            options.data.vault_thread.join()
        room = random.choice([x for x in options.data.vaults_data if x.size < self.vault_max_size])

        return room

    def generate_room_square(self, padding=1):
        room_width = random.randint(self.square_room_min_size, self.square_room_max_size)
        room_height = random.randint(max(int(room_width * 0.5), self.square_room_min_size),
                                     min(int(room_width * 1.5), self.square_room_max_size))

        room = np.zeros((room_height, room_width), dtype=np.int32)
        # If padding > 0, pad the room with walls
        if padding > 0:
            padded_room = np.pad(room, 1, constant_values=1)
        else:
            padded_room = room

        return padded_room

    def generate_room_cellular(self):
        """Return the next step of the cave generation algorithm.

        `tiles` is the input array. (0: wall, 1: floor)

        If the 3x3 area around a tile (including itself) has `wall_rule` number of
        walls then the tile will become a wall.
        """
        convolve_steps = self.cellular_iterations
        rng = np.random.default_rng()
        h = random.randint(self.cross_room_min_size, self.cellular_room_max_size)
        w = random.randint(self.cross_room_min_size, self.cellular_room_max_size)
        arr = rng.choice(2, (h, w),
                         p=[1 - self.cellular_wall_probability, self.cellular_wall_probability])
        room = np.pad(arr, 1, constant_values=1)

        kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]  # 8-bit

        for _ in range(convolve_steps):
            neighbors = convolve2d(room == 0, kernel, "same")
            room = np.where(neighbors < self.cellular_neighbors, 0, 1)  # Apply the wall rule.
            room[[0, -1], :] = 1  # Ensure surrounding wall.
            room[:, [0, -1]] = 1

        # Remove isolated cells with flood fill
        room = self.floodfill_by_xy_scipy(room)

        return room


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
            y1_offset = floors[0][0] - 1
            x1_offset = floors[1][0] - 1
            new_room = Room(vault_room.x1 + x1_offset, vault_room.y1 + y1_offset, room_width,
                            room_height, padded_room, id_nr=id_nr, algorithm="vault")
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
