import random

import numpy as np
from scipy.ndimage import label
from scipy.signal import convolve2d
from scipy.spatial import KDTree

import options
from map_gen.algorithms.drunkards import DrunkardsWalk
from map_gen.dungeon import Dungeon, Room


# ==== Room Addition ====
class RoomAddition(Dungeon):
    def __init__(self, map_width=None, map_height=None, only_cellular=False, only_vaults=False,
                 only_squares=False, squares_and_crosses=False, drunkard=False, max_rooms=5, room_max_size=300,
                 build_later=False, first_room_max_size=None):
        super().__init__(map_width=map_width, map_height=map_height)

        self.feature_rooms = []
        self.rooms = []
        self.vaults = []
        self.rooms_list = []
        self.level = []

        self.room_min_size = 30  # min size in number of floor tiles, not height and width
        self.room_max_size = room_max_size  # min size in number of floor tiles, not height and width
        self.feature_room_min_size = 25
        self.feature_room_min_h = 6
        self.feature_room_min_w = 6
        self.max_rooms = max_rooms

        self.build_room_attempts = 500
        self.place_room_attempts = 10
        self.max_tunnel_length = 20

        self.first_room_max_size = None

        self.square_room_max_size = 20
        self.square_room_min_size = 10

        self.cross_room_max_size = 20
        self.cross_room_min_size = 10

        self.cellular_chance = 0.30  # probability that the first room will be a cavern
        self.cellular_room_min_size = 10  # max height and width for cellular automata rooms
        self.cellular_room_max_size = 30  # max height and width for cellular automata rooms

        self.conjoined_room_chance = 0.0  # chance to make room conjoined with other rooms

        self.first_vault_max_size = 1600
        self.vault_size_offset = 200  # After enough rooms are placed, fetch smaller vaults
        self.vault_max_size = 1200

        self.cellular_wall_probability = 0.45
        self.cellular_neighbors = 5
        self.cellular_iterations = 4

        self.square_room_chance = 0.1
        self.cross_room_chance = 0.15
        self.vault_chance = 0.2

        self.feature_cross_room_chance = 0.0
        self.feature_square_room_chance = 0.6
        self.feature_vault_chance = 0.2

        self.only_cellular = only_cellular
        self.only_vaults = only_vaults
        self.only_squares = only_squares
        self.squares_and_crosses = squares_and_crosses
        self.drunkard = drunkard

        self.build_later = build_later

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
            try:
                x = random.randint(2, self.map_width - room_width - 2)
                y = random.randint(2, self.map_height - room_height - 2)
            except ValueError:
                continue
            id_nr = len(self.rooms) + 1
            new_room = Room(x, y, room_width, room_height, room_arr, id_nr=id_nr, algorithm=algorithm,
                            build_later=self.build_later)

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

            self.place_feature(new_room)

            if len(self.rooms) >= self.max_rooms:
                break

        self.connect_caves()
        self.connect_rooms()
        self.connect_vaults_to_features()
        isolated_rooms = self.get_rooms_by_flood_fill()
        if isolated_rooms:
            for isolated_room in isolated_rooms:
                closest_room = self.get_closest_room(isolated_room)
                self.connect_vault_to_nearest(isolated_room, closest_room)

        return self.level

    def get_closest_room(self, isolated_room):
        center_points = [room.center for room in self.feature_rooms]
        tree = KDTree(center_points)
        closest = tree.query(isolated_room.center)[1]
        return self.rooms[closest]


    def generate_room(self, vault_size_offset=0, max_w=None, max_h=None, feature=False):
        algorithm = None
        # select a room type to generate and return that room
        if not feature:
            if self.only_cellular:
                self.conjoined_room_chance = 1.0
                room = self.generate_room_cellular(max_w, max_h)
                return room, "cellular"
            if self.only_vaults:
                vault_size = self.vault_max_size - vault_size_offset
                if max_w and max_h:
                    vault_size = max_w * max_h
                room = self.generate_random_vault(vault_size)
                return room, "vault"
            if self.only_squares:
                room = self.generate_room_square(max_w=max_w, max_h=max_h)
                return room, "square"
            if self.squares_and_crosses:
                choice = random.random()
                if choice < self.vault_chance:
                    room = self.generate_room_square()
                    algorithm = "square"
                else:
                    room = self.generate_room_cross(max_w, max_h)
                    algorithm = "cross"
                return room, algorithm
        if self.rooms:
            # There is at least one room already
            choice = random.random()

            vault_chance = self.vault_chance if not feature else self.feature_vault_chance
            square_room_chance = self.square_room_chance if not feature else self.feature_square_room_chance
            cross_room_chance = self.cross_room_chance if not feature else self.feature_cross_room_chance

            if choice < vault_chance:
                vault_size = self.vault_max_size - vault_size_offset
                if max_w and max_h:
                    vault_size = max_w * max_h
                room = self.generate_random_vault(vault_size)
                algorithm = "vault"

            else:
                if choice < square_room_chance:
                    room = self.generate_room_square(max_w=max_w, max_h=max_h)
                    algorithm = "square"
                elif square_room_chance <= choice < (square_room_chance + cross_room_chance):
                    room = self.generate_room_cross(max_w, max_h)
                    algorithm = "cross"
                else:
                    room = self.generate_room_cellular(max_w, max_h)
                    algorithm = "cellular"

        else:  # it's the first room
            choice = random.random()
            if choice < self.vault_chance:
                room = self.generate_random_vault(self.first_vault_max_size)
                algorithm = "vault"

            else:
                if choice < self.cellular_chance:
                    room = self.generate_room_cellular(max_w, max_h)
                    algorithm = "cellular"
                else:
                    room = self.generate_room_square(max_w, max_h)
                    algorithm = "square"

        return room, algorithm

    def generate_room_cross(self, max_w, max_h):
        if max_w and max_h:
            max_size = min(max_w, max_h)
            min_size = self.feature_room_min_w
        else:
            max_size = self.cross_room_max_size
            min_size = self.cross_room_min_size
            max_w, max_h = max_size, max_size

        room_hor_width = min(int((random.randint(min_size, max_size)) / 2 * 2), max_w)
        room_ver_height = min(int((random.randint(min_size, max_size)) / 2 * 3), max_h)
        room_hor_height = min(int((random.randint(min_size, room_ver_height)) / 2 * 2), max_h)
        room_ver_width = min(int((random.randint(min_size, room_hor_width)) / 2 * 1), max_w)

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

    def generate_room_square(self, max_w, max_h, padding=1):
        room_min_size = self.square_room_min_size
        if max_w and max_h:
            room_max_size = min(max_w, max_h)
            room_min_size = self.feature_room_min_w
        elif len(self.rooms) == 0 and self.first_room_max_size:
            room_max_size = self.first_room_max_size
            max_w, max_h = room_max_size, room_max_size
        else:
            room_max_size = self.square_room_max_size
            max_w, max_h = room_max_size, room_max_size
        room_width = min(random.randint(room_min_size, room_max_size), max_w)
        room_height = min(random.randint(max(int(room_width * 0.5), room_min_size),
                                     min(int(room_width * 1.5), room_max_size)), max_h)

        room = np.zeros((room_height, room_width), dtype=np.int32)
        # If padding > 0, pad the room with walls
        if padding > 0:
            padded_room = np.pad(room, 1, constant_values=1)
        else:
            padded_room = room

        return padded_room

    def generate_room_cellular(self, max_w, max_h):
        """Return the next step of the cave generation algorithm.

        `tiles` is the input array. (0: wall, 1: floor)

        If the 3x3 area around a tile (including itself) has `wall_rule` number of
        walls then the tile will become a wall.
        """
        convolve_steps = self.cellular_iterations
        rng = np.random.default_rng()
        max_width = max_w if max_w is not None else self.cellular_room_max_size
        max_height = max_h if max_h is not None else self.cellular_room_max_size
        h = random.randint(min(max_height - 1, self.cellular_room_min_size), max_height)
        w = random.randint(min(max_width - 1, self.cellular_room_min_size), max_width)
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

    def get_rooms_by_flood_fill(self, vault_room=None):

        rooms = []
        if not vault_room:
            room_arr = self.level
        else:
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
            id_nr = len(self.rooms) + 1 + len(self.vaults)
            room_height, room_width = padded_room.shape
            y1_offset = floors[0][0] - 1
            x1_offset = floors[1][0] - 1
            if vault_room:
                x1 = vault_room.x1 + x1_offset
                y1 = vault_room.y1 + y1_offset
            else:
                x1 = x1_offset
                y1 = y1_offset
            new_room = Room(x1, y1, room_width,
                            room_height, padded_room, id_nr=id_nr, algorithm="vault")
            rooms.append(new_room)
            self.vaults.append(new_room)

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

    def place_feature(self, parent_room):
        for r in range(self.build_room_attempts * 2):
            max_w = parent_room.w - 3
            max_h = parent_room.h - 3
            if max_h < self.feature_room_min_h or max_w < self.feature_room_min_w:
                continue
            room_arr, algorithm = self.generate_room(1200, max_w, max_h, feature=True)

            room_height, room_width = room_arr.shape
            if room_height >= parent_room.h - 1 or room_width >= parent_room.w - 1:
                continue

            try:
                x = random.randint(parent_room.x1 + 2, parent_room.x2 - room_width - 2)
                y = random.randint(parent_room.y1 + 2, parent_room.y2 - room_height - 2)
            except ValueError:
                continue

            id_nr = len(self.feature_rooms) + 1
            feature_room = Room(x, y, room_width, room_height, room_arr, id_nr=id_nr, algorithm=algorithm,
                                feature=True, parent_room=parent_room)
            if feature_room.size > parent_room.size:
                continue
            parent_room.feature_room = feature_room

            self.add_room(feature_room, feature=True)
            break
