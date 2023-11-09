'''
=============================
Dungeon Generation Algorithms
=============================

Algorithms originally implemented by AtTheMatinee:
https://github.com/AtTheMatinee/dungeon-generation
MIT License
Copyright (c) 2017 AtTheMatinee

Modifications by delamorte.
MIT License
Copyright (c) 2020 delamorte

'''

import random
import xml.etree.ElementTree as ET
from math import sqrt

import numpy as np
from scipy.signal import convolve2d
from tcod import tcod

from color_functions import random_color


class Dungeon:
    def __init__(self, map_width=None, map_height=None):
        self.map_width = map_width
        self.map_height = map_height
        self._currentRegion = None
        self._regions = None
        self.rooms = []
        self.level = []

    def add_room(self, room):
        self.level[room.y1:room.y1 + room.h, room.x1:room.x1 + room.w] = room.nd_array
        self.rooms.append(room)

    def clean_up_map(self, map_width, map_height, smoothing=None, filling=None, iterations=5):
        if smoothing:
            for i in range(iterations):
                # Look at each cell individually and check for smoothness
                for x in range(1, map_width - 1):
                    for y in range(1, map_height - 1):
                        if (self.level[y][x] == 1) and (self.get_adjacent_walls_simple(x, y) <= smoothing):
                            self.level[y][x] = 0

                        if filling and (self.level[x][y] == 0) and (self.get_adjacent_walls_simple(x, y) >= filling):
                            self.level[y][x] = 1

    def get_adjacent_walls_simple(self, x, y):  # finds the walls in four directions
        return self.get_neighbours(x, y, wall_count=True)

    def get_adjacent_walls(self, x, y, room=None):  # finds the walls in 8 directions
        return self.get_neighbours(x, y, pattern="8bit", wall_count=True)

    def adjacent_rooms_scan(self, max_length=20):
        """
        Scan for nearby rooms, then check if a walkable path shorter than 10 exists between the rooms and
        add to adjacent rooms.
        """
        for current_room in self.rooms:
            walls = current_room.outer
            for wall in walls:
                wall_x, wall_y = wall[0], wall[1]
                if self.level[wall_y][wall_x] == 0:
                    for adjacent_room in self.rooms:
                        if current_room != adjacent_room:
                            north = (wall_x, wall_y - 3)
                            south = (wall_x, wall_y + 3)
                            east = (wall_x + 3, wall_y)
                            west = (wall_x - 3, wall_y)

                            for direction in [north, south, east, west]:
                                dir_x, dir_y = direction[0], direction[1]
                                if adjacent_room.x1 <= dir_x <= adjacent_room.x2 and adjacent_room.y1 <= dir_y <= adjacent_room.y2:
                                    start, target = (wall_x, wall_y), (dir_x, dir_y)
                                    path = self.get_path_to(start, target)
                                    if path and len(path) < max_length:
                                        if adjacent_room.id_nr not in current_room.adjacent_room_ids:
                                            current_room.adjacent_room_ids.append(adjacent_room.id_nr)
                                        if current_room.id_nr not in adjacent_room.adjacent_room_ids:
                                            adjacent_room.adjacent_room_ids.append(current_room.id_nr)

        for room in self.rooms:
            print("current room: {0}, adjacent rooms: {1}".format(room.id_nr, room.adjacent_room_ids))

    def adjacent_rooms_path_scan(self, max_length=20):
        """
        Compare room to other rooms, pick two random points and get the shortest path. If path < 10, add room to
        adjacent rooms.
        """
        for current_room in self.rooms:
            for adjacent_room in self.rooms:
                if current_room != adjacent_room:
                    for point1 in current_room.cave:
                        break  # get an element from cave1
                    for point2 in adjacent_room.cave:
                        break  # get an element from cave1
                    path = self.get_path_to(point1, point2)
                    if path and len(path) < max_length:
                        if adjacent_room.id_nr not in current_room.adjacent_room_ids:
                            current_room.adjacent_room_ids.append(adjacent_room.id_nr)
                        if current_room.id_nr not in adjacent_room.adjacent_room_ids:
                            adjacent_room.adjacent_room_ids.append(current_room.id_nr)

        for room in self.rooms:
            print("current room: {0}, adjacent rooms: {1}".format(room.id_nr, room.adjacent_room_ids))

    def get_path_to(self, start, target):
        """Compute and return a path to the target position.
        If there is no valid path then returns an empty list.
        """
        start_x, start_y = start[0], start[1]
        target_x, target_y = target[0], target[1]
        # Copy the walkable array.
        game_map = np.array(self.level)
        walkable = np.frompyfunc(lambda tile: tile == 0, 1, 1)
        cost = np.array(walkable(game_map), dtype=np.int8)

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((start_x, start_y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path = list(pathfinder.path_to((target_x, target_y))[1:])

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(int(index[0]), int(index[1])) for index in path]

    def get_caves(self):
        # locate all the caves within self.level and store them in self.rooms
        for x in range(0, self.map_width):
            for y in range(0, self.map_height):
                if self.level[y][x] == 0:
                    self.flood_fill(x, y)

        for room in self.rooms:
            inner = room.inner
            for tile in inner:
                if self.level[tile[1]][tile[0]] == 1:
                    self.level[tile[1]][tile[0]] = 0

    def flood_fill(self, x, y):
        '''
        flood fill the separate regions of the level, discard
        the regions that are smaller than a minimum size, and
        create a reference for the rest.
        '''
        cave = set()
        walls = set()
        tile = (x, y)
        to_be_filled = {tile}
        while to_be_filled:
            tile = to_be_filled.pop()

            if tile not in cave:
                cave.add(tile)

                self.level[tile[1]][tile[0]] = 1

                # check adjacent cells
                x = tile[0]
                y = tile[1]
                north = (x, y - 1)
                south = (x, y + 1)
                east = (x + 1, y)
                west = (x - 1, y)
                northeast = (x + 1, y - 1)
                southeast = (x + 1, y + 1)
                southwest = (x - 1, y + 1)
                northwest = (x - 1, y - 1)

                for direction in [north, south, east, west, northeast, southeast, southwest, northwest]:

                    if self.level[direction[1]][direction[0]] == 0:
                        if direction not in to_be_filled and direction not in cave:
                            to_be_filled.add(direction)
                    elif self.level[direction[1]][direction[0]] == 1:
                        if direction not in walls and direction not in to_be_filled and direction not in cave:
                            walls.add(direction)

        if self.room_min_size <= len(cave) <= 300:

            x1 = min(cave, key=lambda t: t[0])[0]
            x2 = max(cave, key=lambda t: t[0])[0]
            y1 = min(cave, key=lambda t: t[1])[1]
            y2 = max(cave, key=lambda t: t[1])[1]
            w = x2 - x1
            h = y2 - y1
            id_nr = len(self.rooms) + 1

            room = Room(x1=x1, y1=y1, w=w, h=h, id_nr=id_nr)
            self.rooms.append(room)

    def connect_rooms(self):
        for idx in range(len(self.rooms) - 1):
            room_1 = self.rooms[idx]
            room_2 = self.rooms[idx + 1]
            for x, y in self.tunnel_between(room_2.center, room_1.center):
                self.level[y][x] = 0
                coords = (x, y)
                if coords in room_1.outer and coords not in room_1.entrances:
                    room_1.entrances.add(coords)
                if coords in room_2.outer and coords not in room_2.entrances:
                    room_2.entrances.add(coords)

    def tunnel_between(self, start, end):
        """Return an L-shaped tunnel between these two points."""
        x1, y1 = start
        x2, y2 = end
        if random.random() < 0.5:  # 50% chance.
            # Move horizontally, then vertically.
            corner_x, corner_y = x2, y1
        else:
            # Move vertically, then horizontally.
            corner_x, corner_y = x1, y2

        # Generate the coordinates for this tunnel.
        for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
            yield x, y
        for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
            yield x, y

    def connect_caves(self):
        # Find the closest cave to the current cave
        for current_cave_room in self.rooms:
            current_cave = current_cave_room.inner
            for point1 in current_cave:
                break  # get an element from cave1
            point2 = None
            distance = None
            for next_cave_room in self.rooms:
                next_cave = next_cave_room.inner
                if next_cave != current_cave and not self.check_connectivity(current_cave, next_cave):
                    # choose a random point from next_cave
                    for next_point in next_cave:
                        break  # get an element from cave2
                    # compare distance of point1 to old and new point2
                    new_distance = self.distance_formula(point1, next_point)
                    if new_distance is not None and distance is not None and (
                            new_distance < distance) or distance is None:
                        point2 = next_point
                        distance = new_distance

            if point2:  # if all tunnels are connected, point2 == None
                self.create_tunnel(point1, point2, current_cave_room)

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
                    if direction[1] < self.map_height and direction[0] < self.map_width:
                        if self.level[direction[1]][direction[0]] == 0:
                            if direction not in to_be_filled and direction not in connected_region:
                                to_be_filled.add(direction)

        for end in cave2:
            break  # get an element from cave2

        if end in connected_region:
            return True

        else:
            return False

    def get_neighbours(self, x, y, a=None, radius=1, pattern="4bit", wall_count=False):
        if not a:
            a = self.level
        patterns_map = {
            "4bit": [[0, 1, 0],
                     [1, 0, 1],
                     [0, 1, 0]],
            "8bit": [[1, 1, 1],
                     [1, 0, 1],
                     [1, 1, 1]]
        }
        kernel = patterns_map[pattern]
        if radius > 1:
            kernel = np.pad(kernel, radius-1, mode='edge')
        mask = np.zeros_like(a, dtype=bool)  # build empty mask
        mask[x, y] = True  # set target(s)

        # boolean indexing
        neighbors = a[convolve2d(mask, kernel, mode='same').astype(bool)]
        if wall_count:
            return np.count_nonzero(neighbors)
        return neighbors

    def create_tunnel(self, point1, point2, current_cave_room):
        # run a heavily weighted random Walk
        # from point1 to point2
        drunkard_x = point2[0]
        drunkard_y = point2[1]
        current_cave = current_cave_room.inner
        current_cave_walls = current_cave_room.outer
        current_cave_tunnel = current_cave_room.tunnel
        current_cave_entrances = current_cave_room.entrances

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
                if self.level[drunkard_y][drunkard_x] == 1:
                    self.level[drunkard_y][drunkard_x] = 0
                    wall = (drunkard_x, drunkard_y)
                    current_cave_tunnel.add(wall)
                    if wall in current_cave_walls and wall not in current_cave_entrances:
                        current_cave_entrances.add(wall)

    @staticmethod
    def distance_formula(point1, point2):
        d = sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        return d


class Room:
    def __init__(self, x1=0, y1=0, w=0, h=0, nd_array=None,
                 wall_color="dark gray", floor_color="darkest amber", feature=None,
                 wall_type="wall_brick", floor_type="floor", tiled=False, name=None, lightness=1.0,
                 id_nr=1):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.w = int(w)
        self.h = int(h)
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h
        self.nd_array = nd_array
        self.floor_type = floor_type
        self.wall_type = wall_type
        self.tunnel = set()
        self.entrances = set()
        self.has_door = False
        self.wall_color = wall_color
        self.floor_color = floor_color
        self.feature = feature
        self.tiled = tiled
        self.name = name
        self.lightness = lightness
        # ids used for labeling/maps
        self.id_nr = id_nr
        self.id_color = random_color()
        self.adjacent_room_ids = []
        self.inner = set()
        self.outer = set()
        self.set_inner()
        self.set_outer()
        self.center = self.center()

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    def set_inner(self):
        """Save the inner area of this room as a set of coordinates."""
        inner = np.where(self.nd_array == 0)
        for i in range(inner[0].size):
            y, x = inner[0][i], inner[1][i]
            self.inner.add((int(x+self.x1), int(y+self.y1)))

    def set_outer(self):
        """Save the outer area (walls) of this room as a set of coordinates."""
        outer = np.where(self.nd_array == 1)
        for i in range(outer[0].size):
            y, x = outer[0][i], outer[1][i]
            self.outer.add((int(x+self.x1), int(y+self.y1)))

    def intersects(self, other, inner=False):
        """Return True if this room overlaps with another room.
        :param other: other room
        :param inner: if true, check intersection of inner (floor) tiles
        """
        if inner:
            intersection = self.inner.intersection(other.inner)
            if intersection:
                self.outer -= other.inner
                self.outer -= other.outer
                self.inner -= other.inner
                self.inner -= other.outer
            return bool(intersection)
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


class TiledRoom(Room):
    def __init__(self, x1=0, y1=0, w=0, h=0, wall_color="dark gray", floor_color="darkest amber",
                 floor="floor", tiled=True, name=None, lightness=1.0, filename=None):
        Room.__init__(self, x1=x1, y1=y1, w=w, h=h, wall_color=wall_color, floor_color=floor_color,
                      floor=floor, tiled=tiled, name=name, lightness=lightness)
        self.layers = None
        self.tiled_reader(filename)

    def tiled_reader(self, name):
        tree = ET.parse("./resources/prefabs/" + name + ".tmx")
        root = tree.getroot()
        layers = [None, None, None]

        # Parse custom properties, not used atm
        # custom_properties = {}
        # for tile in root.iter("tile"):
        #     tile_id = tile.get("id")
        #     for tile_property in tile.findall("property"):
        #         property_name = tile_property.get("name")
        #         property_value = tile_property.get("value")
        #         custom_properties[tile_id] = [property_name, property_value]

        for layer in root.iter("layer"):

            data = layer.find("data").text[1:-1].splitlines()
            self.h = len(data)
            self.w = len(data[0].split(",")) - 1
            tiled_map = []
            for row in data:
                if row[-1] == ",":
                    new_row = row.split(",")[:-1]
                else:
                    new_row = row.split(",")
                for i, char in enumerate(new_row):
                    value = int(char) - 1 if int(char) > 0 else 0
                    new_row[i] = value

                tiled_map.append(new_row)

            layers[int(layer.attrib["name"])] = tiled_map

        self.layers = layers


class Rect:
    def __init__(self, x, y, w, h, nd_array=None):
        self.x1 = x
        self.y1 = y
        self.x2 = x+w
        self.y2 = y+h
        self.width = w
        self.height = h
        self.nd_array = nd_array

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    def inner(self):
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other):
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


class Leaf:  # used for the BSP tree algorithm
    def __init__(self, x, y, width, height):
        self.room_2 = None
        self.room_1 = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.MIN_LEAF_SIZE = 10
        self.child_1 = None
        self.child_2 = None
        self.room = None
        self.hall = None

    def split_leaf(self):
        # begin splitting the leaf into two children
        if (self.child_1 is not None) or (self.child_2 is not None):
            return False  # This leaf has already been split

        '''
        ==== Determine the direction of the split ====
        If the width of the leaf is >25% larger than the height,
        split the leaf vertically.
        If the height of the leaf is >25 larger than the width,
        split the leaf horizontally.
        Otherwise, choose the direction at random.
        '''
        split_horizontally = random.choice([True, False])
        if self.width / self.height >= 1.25:
            split_horizontally = False
        elif self.height / self.width >= 1.25:
            split_horizontally = True

        if split_horizontally:
            max_size = self.height - self.MIN_LEAF_SIZE
        else:
            max_size = self.width - self.MIN_LEAF_SIZE

        if max_size <= self.MIN_LEAF_SIZE:
            return False  # the leaf is too small to split further

        split = random.randint(self.MIN_LEAF_SIZE, max_size)  # determine where to split the leaf

        if split_horizontally:
            self.child_1 = Leaf(self.x, self.y, self.width, split)
            self.child_2 = Leaf(self.x, self.y + split, self.width, self.height - split)
        else:
            self.child_1 = Leaf(self.x, self.y, split, self.height)
            self.child_2 = Leaf(self.x + split, self.y, self.width - split, self.height)

        return True

    def create_rooms(self, bsp_tree, ext_walls=True):
        if self.child_1 or self.child_2:
            # recursively search for children until you hit the end of the branch
            if self.child_1:
                self.child_1.create_rooms(bsp_tree)
            if self.child_2:
                self.child_2.create_rooms(bsp_tree)

            if self.child_1 and self.child_2:
                bsp_tree.createHall(self.child_1.get_room(),
                                    self.child_2.get_room())

        else:
            # Create rooms in the end branches of the bsp tree
            self.room = bsp_tree.create_room_from_rectangle(self)

    def get_room(self):
        if self.room:
            return self.room

        else:
            if self.child_1:
                self.room_1 = self.child_1.get_room()
            if self.child_2:
                self.room_2 = self.child_2.get_room()

            if not self.child_1 and not self.child_2:
                # neither room_1 nor room_2
                return None

            elif not self.room_2:
                # room_1 and !room_2
                return self.room_1

            elif not self.room_1:
                # room_2 and !room_1
                return self.room_2

            # If both room_1 and room_2 exist, pick one
            elif random.random() < 0.5:
                return self.room_1
            else:
                return self.room_2
