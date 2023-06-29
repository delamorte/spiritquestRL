import random
from math import sqrt


# ==== Cellular Automata ====
class CellularAutomata:
    '''
    Rather than implement a traditional cellular automata, I
    decided to try my hand at a method discribed by "Evil
    Scientist" Andy Stobirski that I recently learned about
    on the Grid Sage Games blog.
    '''

    def __init__(self):
        self.level = []
        self.rooms = []

        self.iterations = 10000
        self.neighbors = 3  # number of neighboring walls for this cell to become a wall
        self.wallProbability = 0.45  # the initial probability of a cell becoming a wall, recommended to be between .35 and .55

        self.ROOM_MIN_SIZE = 16  # size in total number of cells, not dimensions
        self.ROOM_MAX_SIZE = 500  # size in total number of cells, not dimensions

        self.smoothEdges = True
        self.smoothing = 1
        self.name = "CellularAutomata"

    def generate_level(self, map_width, map_height):
        # Creates an empty 2D array or clears existing array
        self.level = [[1
                       for y in range(map_height)]
                      for x in range(map_width)]

        self.randomFillMap(map_width, map_height)
        self.createCaves(map_width, map_height)
        self.getCaves(map_width, map_height)
        self.connectCaves(map_width, map_height)
        self.cleanUpMap(map_width, map_height)
        return self.level

    def randomFillMap(self, map_width, map_height):
        for y in range(1, map_height - 1):
            for x in range(1, map_width - 1):
                # print("(",x,y,") = ",self.level[x][y])
                if random.random() >= self.wallProbability:
                    self.level[x][y] = 0

    def createCaves(self, map_width, map_height):
        # ==== Create distinct caves ====
        for i in range(0, self.iterations):
            # Pick a random point with a buffer around the edges of the map
            tile_x = random.randint(1, map_width - 2)
            tile_y = random.randint(1, map_height - 2)

            adjacent_walls = self.getAdjacentWalls(tile_x, tile_y)

            # if the cell's neighboring walls > self.neighbors, set it to 1
            if adjacent_walls > self.neighbors:
                self.level[tile_x][tile_y] = 1
            # or set it to 0
            elif adjacent_walls < self.neighbors:
                self.level[tile_x][tile_y] = 0

        # ==== Clean Up Map ====
        self.cleanUpMap(map_width, map_height)

    def cleanUpMap(self, map_width, map_height):
        if (self.smoothEdges):
            for i in range(0, 5):
                # Look at each cell individually and check for smoothness
                for x in range(1, map_width - 1):
                    for y in range(1, map_height - 1):
                        if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x, y) <= self.smoothing):
                            self.level[x][y] = 0

    def createTunnel(self, point1, point2, currentCave, map_width, map_height):
        # run a heavily weighted random Walk
        # from point1 to point1
        drunkardX = point2[0]
        drunkardY = point2[1]
        while (drunkardX, drunkardY) not in currentCave:
            # ==== Choose Direction ====
            north = 1.0
            south = 1.0
            east = 1.0
            west = 1.0

            weight = 1

            # weight the random walk against edges
            if drunkardX < point1[0]:  # drunkard is left of point1
                east += weight
            elif drunkardX > point1[0]:  # drunkard is right of point1
                west += weight
            if drunkardY < point1[1]:  # drunkard is above point1
                south += weight
            elif drunkardY > point1[1]:  # drunkard is below point1
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
            if (0 < drunkardX + dx < map_width - 1) and (0 < drunkardY + dy < map_height - 1):
                drunkardX += dx
                drunkardY += dy
                if self.level[drunkardX][drunkardY] == 1:
                    self.level[drunkardX][drunkardY] = 0

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

    def getAdjacentWalls(self, tile_x, tile_y):  # finds the walls in 8 directions
        wallCounter = 0
        for x in range(tile_x - 1, tile_x + 2):
            for y in range(tile_y - 1, tile_y + 2):
                if (self.level[x][y] == 1):
                    if (x != tile_x) or (y != tile_y):  # exclude (tile_x,tile_y)
                        wallCounter += 1
        return wallCounter

    def getCaves(self, map_width, map_height):
        # locate all the caves within self.level and store them in self.rooms
        for x in range(0, map_width):
            for y in range(0, map_height):
                if self.level[x][y] == 0:
                    self.floodFill(x, y)

        for set in self.rooms:
            for tile in set:
                self.level[tile[0]][tile[1]] = 0

    def floodFill(self, x, y):
        '''
        flood fill the separate regions of the level, discard
        the regions that are smaller than a minimum size, and
        create a reference for the rest.
        '''
        cave = set()
        tile = (x, y)
        toBeFilled = set([tile])
        while toBeFilled:
            tile = toBeFilled.pop()

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
                        if direction not in toBeFilled and direction not in cave:
                            toBeFilled.add(direction)

        if self.ROOM_MIN_SIZE <= len(cave) <= self.ROOM_MAX_SIZE:
            self.rooms.append(cave)

    def connectCaves(self, map_width, map_height):
        # Find the closest cave to the current cave
        for currentCave in self.rooms:
            for point1 in currentCave: break  # get an element from cave1
            point2 = None
            distance = None
            for nextCave in self.rooms:
                if nextCave != currentCave and not self.checkConnectivity(currentCave, nextCave):
                    # choose a random point from nextCave
                    for nextPoint in nextCave: break  # get an element from cave1
                    # compare distance of point1 to old and new point2
                    newDistance = self.distanceFormula(point1, nextPoint)
                    if newDistance is not None and distance is not None and (
                            newDistance < distance) or distance == None:
                        point2 = nextPoint
                        distance = newDistance

            if point2:  # if all tunnels are connected, point2 == None
                self.createTunnel(point1, point2, currentCave, map_width, map_height)

    def distanceFormula(self, point1, point2):
        d = sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        return d

    def checkConnectivity(self, cave1, cave2):
        # floods cave1, then checks a point in cave2 for the flood

        connectedRegion = set()
        for start in cave1: break  # get an element from cave1

        toBeFilled = set([start])
        while toBeFilled:
            tile = toBeFilled.pop()

            if tile not in connectedRegion:
                connectedRegion.add(tile)

                # check adjacent cells
                x = tile[0]
                y = tile[1]
                north = (x, y - 1)
                south = (x, y + 1)
                east = (x + 1, y)
                west = (x - 1, y)

                for direction in [north, south, east, west]:

                    if self.level[direction[0]][direction[1]] == 0:
                        if direction not in toBeFilled and direction not in connectedRegion:
                            toBeFilled.add(direction)

        for end in cave2: break  # get an element from cave2

        if end in connectedRegion:
            return True

        else:
            return False
