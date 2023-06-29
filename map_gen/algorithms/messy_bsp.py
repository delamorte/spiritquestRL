import random

from map_gen.dungeon import Leaf, Dungeon


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
        self.ROOM_MAX_SIZE = 15
        self.ROOM_MIN_SIZE = 6
        self.smoothing = 1
        self.filling = 3
        self.clean_up_iterations = 3
        self.name = "MessyBSPTree"

    def generate_level(self):
        # Creates an empty 2D array or clears existing array
        self.map_width = self.map_width
        self.map_height = self.map_height
        self.level = [[1
                       for y in range(self.map_height)]
                      for x in range(self.map_width)]

        self._leafs = []

        rootLeaf = Leaf(0, 0, self.map_width, self.map_height)
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
        self.clean_up_map(self.map_width, self.map_height, smoothing=self.smoothing, filling=self.filling,
                          iterations=self.clean_up_iterations)

        return self.level

    def createHall(self, room1, room2):
        # run a heavily weighted random Walk
        # from point2 to point1
        drunkard_x, drunkard_y = room2.center()
        goalX, goalY = room1.center()
        while not (room1.x1 <= drunkard_x <= room1.x2) or not (room1.y1 < drunkard_y < room1.y2):  #
            # ==== Choose Direction ====
            north = 1.0
            south = 1.0
            east = 1.0
            west = 1.0

            weight = 1

            # weight the random walk against edges
            if drunkard_x < goalX:  # drunkard is left of point1
                east += weight
            elif drunkard_x > goalX:  # drunkard is right of point1
                west += weight
            if drunkard_y < goalY:  # drunkard is above point1
                south += weight
            elif drunkard_y > goalY:  # drunkard is below point1
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
            # check colision at edges
            if (0 < drunkard_x + dx < self.self.map_width - 1) and (0 < drunkard_y + dy < self.self.map_height - 1):
                drunkard_x += dx
                drunkard_y += dy
                if self.level[int(drunkard_x)][int(drunkard_y)] == 1:
                    self.level[int(drunkard_x)][int(drunkard_y)] = 0
