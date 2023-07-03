# ==== BSP Tree ====
import random

from map_gen.dungeon import Leaf, Dungeon


class BSPTree(Dungeon):
    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.room = None
        self.MAX_LEAF_SIZE = 24
        self.ROOM_MAX_SIZE = 15
        self.ROOM_MIN_SIZE = 6
        self.name = "BSPTree"

    def generate_level(self, map_width, map_height):
        # Creates an empty 2D array or clears existing array
        self.level = [[1
                       for y in range(map_height)]
                      for x in range(map_width)]

        self._leafs = []

        rootLeaf = Leaf(0, 0, map_width, map_height)
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

        return self.level

    def createHall(self, room1, room2):
        # connect two rooms by hallways
        x1, y1 = room1.get_center()
        x2, y2 = room2.get_center()
        # 50% chance that a tunnel will start horizontally
        if random.randint(0, 1) == 1:
            self.createHorTunnel(x1, x2, y1)
            self.createVirTunnel(y1, y2, x2)

        else:  # else it starts virtically
            self.createVirTunnel(y1, y2, x1)
            self.createHorTunnel(x1, x2, y2)

    def createHorTunnel(self, x1, x2, y):
        y = int(y)
        for x in range(int(min(x1, x2)), int(max(x1, x2) + 1)):
            self.level[x][y] = 0

    def createVirTunnel(self, y1, y2, x):
        x = int(x)
        for y in range(int(min(y1, y2)), int(max(y1, y2) + 1)):
            self.level[x][y] = 0
