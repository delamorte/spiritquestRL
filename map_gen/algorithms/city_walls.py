import random

from map_gen.dungeon import Leaf, Dungeon


# ==== City Walls ====
class CityWalls(Dungeon):
    '''
    The City Walls algorithm is very similar to the BSP Tree
    above. In fact their main difference is in how they generate
    rooms after the actual tree has been created. Instead of
    starting with an array of solid walls and carving out
    rooms connected by tunnels, the City Walls generator
    starts with an array of floor tiles, then creates only the
    exterior of the rooms, then opens one wall for a door.
    '''

    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.room = None
        self.MAX_LEAF_SIZE = 30
        self.ROOM_MAX_SIZE = 16
        self.ROOM_MIN_SIZE = 8
        self.name = "CityWalls"

    def generate_level(self, map_width, map_height):
        # Creates an empty 2D array or clears existing array
        self.level = [[0
                       for y in range(map_height)]
                      for x in range(map_width)]

        self._leafs = []
        self.rooms = []

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

        rootLeaf.create_rooms(self, ext_walls=True)
        self.createDoors()

        return self.level


    def createDoors(self):
        for room in self.rooms:
            (x, y) = room.center()

            wall = random.choice(["north", "south", "east", "west"])
            if wall == "north":
                wallX = x
                wallY = room.y1 + 1
            elif wall == "south":
                wallX = x
                wallY = room.y2 - 1
            elif wall == "east":
                wallX = room.x2 - 1
                wallY = y
            elif wall == "west":
                wallX = room.x1 + 1
                wallY = y

            self.level[int(wallX)][int(wallY)] = 0

    def createHall(self, room1, room2):
        # This method actually creates a list of rooms,
        # but since it is called from an outside class that is also
        # used by other dungeon Generators, it was simpler to
        # repurpose the createHall method that to alter the leaf class.
        for room in [room1, room2]:
            if room not in self.rooms:
                self.rooms.append(room)

