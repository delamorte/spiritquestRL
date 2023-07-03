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

from color_functions import random_color


class Dungeon:
    def __init__(self, map_width=None, map_height=None):
        self.map_width = map_width
        self.map_height = map_height
        self._currentRegion = None
        self._regions = None
        self.rooms = []
        self.level = []

    def create_room_rect(self, room, ext_walls=False, carve=False):
        '''
        :param room: Rectangle
        :param ext_walls: If true, set outer tiles to 1 and interior to 0. If false, set all tiles to 0.
        :param carve: Used for maze_with_rooms
        '''
        cave = set()
        for x in range(room.x1, room.x2):
            for y in range(room.y1, room.y2):
                if carve:
                    self.carve(x, y)
                self.level[x][y] = 0
                if ext_walls:
                    if (y == room.y1 or y == room.y2 - 1) and 0 <= x <= room.x2 - 1:
                        self.level[x][y] = 1
                    elif (x == room.x1 or x == room.x2 - 1) and 0 <= y < room.y2 - 1:
                        self.level[x][y] = 1
                cave.add((x, y))
        self.rooms.append(cave)

    def carve(self, x, y):
        self._regions[x][y] = self._currentRegion

    def clean_up_map(self, map_width, map_height, smoothing=None, filling=None, iterations=5):
        if smoothing:
            for i in range(iterations):
                # Look at each cell individually and check for smoothness
                for x in range(1, map_width - 1):
                    for y in range(1, map_height - 1):
                        if (self.level[x][y] == 1) and (self.get_adjacent_walls_simple(x, y) <= smoothing):
                            self.level[x][y] = 0

                        if filling and (self.level[x][y] == 0) and (self.get_adjacent_walls_simple(x, y) >= filling):
                            self.level[x][y] = 1

    def get_adjacent_walls_simple(self, x, y):  # finds the walls in four directions
        wall_counter = 0
        # print("(",x,",",y,") = ",self.level[x][y])
        if self.level[x][y - 1] == 1:  # Check north
            wall_counter += 1
        if self.level[x][y + 1] == 1:  # Check south
            wall_counter += 1
        if self.level[x - 1][y] == 1:  # Check west
            wall_counter += 1
        if self.level[x + 1][y] == 1:  # Check east
            wall_counter += 1

        return wall_counter

    def get_adjacent_walls(self, tile_x, tile_y, room=None):  # finds the walls in 8 directions
        wall_counter = 0
        if room is None:
            room = self.level
        for x in range(tile_x - 1, tile_x + 2):
            for y in range(tile_y - 1, tile_y + 2):
                if room[x][y] == 1:
                    if (x != tile_x) or (y != tile_y):  # exclude (tile_x,tile_y)
                        wall_counter += 1
        return wall_counter

    @staticmethod
    def distance_formula(point1, point2):
        d = sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        return d

# ==== Helper Classes ====
class Room:
    def __init__(self, x1=0, y1=0, x2=0, y2=0, w=0, h=0, wall_color="dark gray", floor_color="darkest amber",
                 wall="wall_brick", floor="floor", tiled=False, name=None, lightness=1.0, cave=None,
                 id_nr=1):
        self.x1 = x1
        self.y1 = y1
        self.w = w
        self.h = h
        if cave:
            self.x2 = x2
            self.y2 = y2
        else:
            self.x2 = self.x1 + self.w
            self.y2 = self.y1 + self.h
        self.floor = floor
        self.wall = wall
        self.wall_color = wall_color
        self.floor_color = floor_color
        self.tiled = tiled
        self.name = name
        self.lightness = lightness
        self.cave = cave
        # ids used for labeling/maps
        self.id_nr = id_nr
        self.id_color = random_color()

    def update_coordinates(self, x1, y1):
        self.x1 = x1
        self.y1 = y1
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h

    def get_room_tiles(self):

        area = []

        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                area.append((x, y))

        return area

    def get_walls(self):

        walls = []

        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                if (x == self.x1 or x == self.x2 - 1 or
                        y == self.y1 or y == self.y2 - 1):
                    walls.append((x, y))

        return walls

    def get_center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return center_x, center_y

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class TiledRoom(Room):
    def __init__(self, x1=0, y1=0, w=0, h=0, wall_color="dark gray", floor_color="darkest amber",
                 floor="floor", tiled=True, name=None, lightness=1.0, filename=None):
        Room.__init__(self, x1=x1, y1=y1, w=w, h=h, wall_color=wall_color, floor_color=floor_color,
                      floor=floor, tiled=tiled, name=name, lightness=lightness)
        self.layers = None
        self.tiled_reader(filename)

    def tiled_reader(self, name):
        tree = ET.parse("./maps/" + name + ".tmx")
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

    def create_rooms(self, bsp_tree, ext_walls=False):
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
            w = random.randint(bsp_tree.ROOM_MIN_SIZE, min(bsp_tree.ROOM_MAX_SIZE, self.width - 1))
            h = random.randint(bsp_tree.ROOM_MIN_SIZE, min(bsp_tree.ROOM_MAX_SIZE, self.height - 1))
            x = random.randint(self.x, self.x + (self.width - 1) - w)
            y = random.randint(self.y, self.y + (self.height - 1) - h)
            self.room = Room(x, y, w, h)
            bsp_tree.create_room_rect(self.room, ext_walls=ext_walls)

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
