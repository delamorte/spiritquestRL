import random

import numpy as np

from map_gen.dungeon import Dungeon, Room, Rect


# ==== Messy BSP Tree ====
class MessyBSPTree(Dungeon):
    '''
    A Binary Space Partition connected by a severely weighted
    drunkards walk algorithm.
    Requires Leaf and Rect classes.
    '''

    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.rooms = []
        self.MAX_LEAF_SIZE = 24
        self.room_max_size = 15
        self.room_min_size = 6
        self.smoothing = 1
        self.filling = 3
        self.clean_up_iterations = 3
        self.name = "MessyBSPTree"

    def generate_level(self):
        # Creates an empty 2D array or clears existing array
        self.map_width = self.map_width
        self.map_height = self.map_height
        self.level = np.ones((self.map_height, self.map_width), dtype=np.int32)
        self._leafs = []

        rootLeaf = Leaf(2, 2, self.map_width-2, self.map_height-2)
        self._leafs.append(rootLeaf)

        splitSuccessfully = True
        # loop through all leaves until they can no longer split successfully
        while (splitSuccessfully):
            splitSuccessfully = False
            for l in self._leafs:
                if (l.child_1 == None) and (l.child_2 == None):
                    if ((l.width > self.MAX_LEAF_SIZE) or
                            (l.height > self.MAX_LEAF_SIZE) or
                            (random.random() > 0.8)):
                        if (l.split_leaf()):  # try to split the leaf
                            self._leafs.append(l.child_1)
                            self._leafs.append(l.child_2)
                            splitSuccessfully = True

        rootLeaf.create_rooms(self)
        self.connect_caves()
        self.clean_up_map(self.map_width, self.map_height, smoothing=self.smoothing, filling=self.filling,
                          iterations=self.clean_up_iterations)
        #self.adjacent_rooms_path_scan(max_length=20)
        return self.level

    def create_room_from_rectangle(self, leaf):
        w = random.randint(self.room_min_size, min(self.room_max_size, leaf.width - 1))
        h = random.randint(self.room_min_size, min(self.room_max_size, leaf.height - 1))
        x = random.randint(leaf.x, leaf.x + (leaf.width - 1) - w)
        y = random.randint(leaf.y, leaf.y + (leaf.height - 1) - h)

        room_arr = np.ones((h, w), dtype=np.int32)
        room_arr[1:-1, 1:-1] = 0
        id_nr = len(self.rooms) + 1

        room = Room(x1=x, y1=y, w=w, h=h, nd_array=room_arr,
                    id_nr=id_nr)
        self.add_room(room)
        return room

    def createHall(self, room1, room2):
        # run a heavily weighted random Walk
        # from point2 to point1
        drunkard_x, drunkard_y = room2.center
        goal_x, goal_y = room1.center
        while not (room1.x1 <= drunkard_x <= room1.x2) or not (room1.y1 < drunkard_y < room1.y2):  #
            # ==== Choose Direction ====
            north = 1.0
            south = 1.0
            east = 1.0
            west = 1.0

            weight = 1

            # weight the random walk against edges
            if drunkard_x < goal_x:  # drunkard is left of point1
                east += weight
            elif drunkard_x > goal_x:  # drunkard is right of point1
                west += weight
            if drunkard_y < goal_y:  # drunkard is above point1
                south += weight
            elif drunkard_y > goal_y:  # drunkard is below point1
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
                if self.level[int(drunkard_y)][int(drunkard_x)] == 1:
                    self.level[int(drunkard_y)][int(drunkard_x)] = 0
                    wall = (int(drunkard_x), int(drunkard_y))
                    if wall in room1.outer and wall not in room1.entrances:
                        room1.entrances.add(wall)
                    if wall in room2.outer and wall not in room2.entrances:
                        room2.entrances.add(wall)


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

    def create_rooms(self, bsp_tree):
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
            w = random.randint(bsp_tree.room_min_size, min(bsp_tree.room_min_size, self.width - 1))
            h = random.randint(bsp_tree.room_min_size, min(bsp_tree.room_min_size, self.height - 1))
            x = random.randint(self.x, self.x + (self.width - 1) - w)
            y = random.randint(self.y, self.y + (self.height - 1) - h)
            rect = Rect(x, y, w, h)
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
