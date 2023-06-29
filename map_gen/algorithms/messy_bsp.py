import random

from map_gen.dungeon import Leaf


# ==== Messy BSP Tree ====
class MessyBSPTree:
    '''
    A Binary Space Partition connected by a severely weighted
    drunkards walk algorithm.
    Requires Leaf and Rect classes.
    '''

    def __init__(self):
        self.level = []
        self.rooms = []
        self.room = None
        self.MAX_LEAF_SIZE = 24
        self.ROOM_MAX_SIZE = 15
        self.ROOM_MIN_SIZE = 6
        self.smoothEdges = True
        self.smoothing = 1
        self.filling = 3
        self.name = "MessyBSPTree"

    def generate_level(self, map_width, map_height):
        # Creates an empty 2D array or clears existing array
        self.map_width = map_width
        self.map_height = map_height
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
        self.cleanUpMap(map_width, map_height)

        return self.level

    def createRoom(self, room):
        # set all tiles within a rectangle to 0
        cave = set()
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.level[x][y] = 0
                cave.add((x, y))
        self.rooms.append(cave)

    def createHall(self, room1, room2):
        # run a heavily weighted random Walk
        # from point2 to point1
        drunkardX, drunkardY = room2.center()
        goalX, goalY = room1.center()
        while not (room1.x1 <= drunkardX <= room1.x2) or not (room1.y1 < drunkardY < room1.y2):  #
            # ==== Choose Direction ====
            north = 1.0
            south = 1.0
            east = 1.0
            west = 1.0

            weight = 1

            # weight the random walk against edges
            if drunkardX < goalX:  # drunkard is left of point1
                east += weight
            elif drunkardX > goalX:  # drunkard is right of point1
                west += weight
            if drunkardY < goalY:  # drunkard is above point1
                south += weight
            elif drunkardY > goalY:  # drunkard is below point1
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
            if (0 < drunkardX + dx < self.map_width - 1) and (0 < drunkardY + dy < self.map_height - 1):
                drunkardX += dx
                drunkardY += dy
                if self.level[int(drunkardX)][int(drunkardY)] == 1:
                    self.level[int(drunkardX)][int(drunkardY)] = 0

    def cleanUpMap(self, map_width, map_height):
        if (self.smoothEdges):
            for i in range(3):
                # Look at each cell individually and check for smoothness
                for x in range(1, map_width - 1):
                    for y in range(1, map_height - 1):
                        if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x, y) <= self.smoothing):
                            self.level[x][y] = 0

                        if (self.level[x][y] == 0) and (self.getAdjacentWallsSimple(x, y) >= self.filling):
                            self.level[x][y] = 1

    def getAdjacentWallsSimple(self, x, y):  # finds the walls in four directions
        wallCounter = 0
        # print("(",x,",",y,") = ",self.level[x][y])
        if (self.level[x][y - 1] == 1):  # Check north
            wallCounter += 1
        if (self.level[x][y + 1] == 1):  # Check south
            wallCounter += 1
        if (self.level[x - 1][y] == 1):  # Check west
            wallCounter += 1
        if (self.level[x + 1][y] == 1):  # Check east
            wallCounter += 1

        return wallCounter
