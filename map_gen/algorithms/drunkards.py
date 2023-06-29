import random

from map_gen.dungeon import Dungeon


# ==== Drunkards Walk ====
class DrunkardsWalk(Dungeon):
    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.rooms = None
        self._percentGoal = .6
        self.walkIterations = 25000  # cut off in case _percentGoal in never reached
        self.weightedTowardCenter = 0.15
        self.weightedTowardPreviousDirection = 0.7
        self.name = "DrunkardsWalk"

    def generate_level(self, map_width, map_height):
        # Creates an empty 2D array or clears existing array
        self.walkIterations = max(self.walkIterations, (map_width * map_height * 10))
        self.level = [[1
                       for y in range(map_height)]
                      for x in range(map_width)]

        self._filled = 0
        self._previousDirection = None

        self.drunkard_x = random.randint(2, map_width - 2)
        self.drunkard_y = random.randint(2, map_height - 2)
        self.filledGoal = map_width * map_height * self._percentGoal

        for i in range(self.walkIterations):
            self.walk(map_width, map_height)
            if (self._filled >= self.filledGoal):
                break

        return self.level

    def walk(self, map_width, map_height):
        # ==== Choose Direction ====
        north = 1.0
        south = 1.0
        east = 1.0
        west = 1.0

        # weight the random walk against edges
        if self.drunkard_x < map_width * 0.25:  # drunkard is at far left side of map
            east += self.weightedTowardCenter
        elif self.drunkard_x > map_width * 0.75:  # drunkard is at far right side of map
            west += self.weightedTowardCenter
        if self.drunkard_y < map_height * 0.25:  # drunkard is at the top of the map
            south += self.weightedTowardCenter
        elif self.drunkard_y > map_height * 0.75:  # drunkard is at the bottom of the map
            north += self.weightedTowardCenter

        # weight the random walk in favor of the previous direction
        if self._previousDirection == "north":
            north += self.weightedTowardPreviousDirection
        if self._previousDirection == "south":
            south += self.weightedTowardPreviousDirection
        if self._previousDirection == "east":
            east += self.weightedTowardPreviousDirection
        if self._previousDirection == "west":
            west += self.weightedTowardPreviousDirection

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
            direction = "north"
        elif north <= choice < (north + south):
            dx = 0
            dy = 1
            direction = "south"
        elif (north + south) <= choice < (north + south + east):
            dx = 1
            dy = 0
            direction = "east"
        else:
            dx = -1
            dy = 0
            direction = "west"

        # ==== Walk ====
        # check colision at edges TODO: change so it stops one tile from edge
        if (0 < self.drunkard_x + dx < map_width - 1) and (0 < self.drunkard_y + dy < map_height - 1):
            self.drunkard_x += dx
            self.drunkard_y += dy
            if self.level[self.drunkard_x][self.drunkard_y] == 1:
                self.level[self.drunkard_x][self.drunkard_y] = 0
                self._filled += 1
            self._previousDirection = direction