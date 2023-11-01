import os
import random

from tcod import libtcodpy
from tcod import map as tcod_map

from map_gen.dungeon import Dungeon, Room


# ==== Room Addition ====
class RoomAddition(Dungeon):
    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.rooms = []
        self.rooms_list = []
        self.level = []

        self.ROOM_MAX_SIZE = 18  # max height and width for cellular automata rooms
        self.ROOM_MIN_SIZE = 16  # min size in number of floor tiles, not height and width
        self.MAX_NUM_ROOMS = 30

        self.SQUARE_ROOM_MAX_SIZE = 12
        self.SQUARE_ROOM_MIN_SIZE = 6

        self.CROSS_ROOM_MAX_SIZE = 14
        self.CROSS_ROOM_MIN_SIZE = 4

        self.cavernChance = 0.30  # probability that the first room will be a cavern
        self.CAVERN_MAX_SIZE = 18  # max height an width

        self.wall_probability = 0.45
        self.neighbors = 4

        self.squareRoomChance = 0.1
        self.crossRoomChance = 0.15
        self.vaultChance = 0.40

        self.buildRoomAttempts = 500
        self.placeRoomAttempts = 20
        self.maxTunnelLength = 12

        self.includeShortcuts = True
        self.shortcutAttempts = 500
        self.shortcutLength = 5
        self.minPathfindingDistance = 50

        self.name = "RoomAddition"

    def generate_level(self):

        self.level = [[1
                       for y in range(self.map_height)]
                      for x in range(self.map_width)]

        # generate the first room
        room = self.generateRoom()
        roomWidth, roomHeight = self.get_room_dimensions(room)
        roomX = int((self.map_width / 2 - roomWidth / 2)) - 1
        roomY = int((self.map_height / 2 - roomHeight / 2)) - 1
        self.addRoom(roomX, roomY, room)

        # generate other rooms
        for i in range(self.buildRoomAttempts):
            room = self.generateRoom()
            # try to position the room, get roomX and roomY
            roomX, roomY, wallTile, direction, tunnelLength = self.placeRoom(room, self.map_width, self.map_height)
            if roomX and roomY:
                self.addRoom(roomX, roomY, room)
                #self.addTunnel(wallTile, direction, tunnelLength)
                if len(self.rooms_list) >= self.MAX_NUM_ROOMS:
                    break



        self.get_caves()
        self.connect_caves()
        self.clean_up_map(self.map_width, self.map_height)
        #if self.includeShortcuts == True:
        #    self.addShortcuts(self.map_width, self.map_height)
        self.adjacent_rooms_scan()

        return self.level

    def generateRoom(self):
        # select a room type to generate and return that room
        if self.rooms_list:
            # There is at least one room already
            choice = random.random()

            if choice < self.vaultChance:
                room = self.generateRandomVault()

            else:
                if choice < self.squareRoomChance:
                    room = self.generateRoomSquare()
                elif self.squareRoomChance <= choice < (self.squareRoomChance + self.crossRoomChance):
                    room = self.generateRoomCross()
                else:
                    room = self.generateRoomCavern(max_size=self.ROOM_MAX_SIZE)

        else:  # it's the first room
            choice = random.random()
            if choice < self.vaultChance:
                room = self.generateRandomVault()
            else:
                if choice < self.cavernChance:
                    room = self.generateRoomCavern(max_size=self.CAVERN_MAX_SIZE)
                else:
                    room = self.generateRoomSquare()

        return room

    def generateRoomCross(self):
        room_hor_width = int((random.randint(self.CROSS_ROOM_MIN_SIZE + 2, self.CROSS_ROOM_MAX_SIZE)) / 2 * 2)
        room_ver_height = int((random.randint(self.CROSS_ROOM_MIN_SIZE + 2, self.CROSS_ROOM_MAX_SIZE)) / 2 * 3)
        room_hor_height = int((random.randint(self.CROSS_ROOM_MIN_SIZE, room_ver_height - 2)) / 2 * 2)
        room_ver_width = int((random.randint(self.CROSS_ROOM_MIN_SIZE, room_hor_width - 2)) / 2 * 1)

        room = [[1
                 for y in range(int(room_ver_height))]
                for x in range(int(room_hor_width))]

        # Fill in vertical space
        ver_offset = int(room_ver_height / 2 - room_hor_height / 2)
        for y in range(ver_offset, room_hor_height + ver_offset):
            for x in range(0, int(room_hor_width)):
                room[x][y] = 0

        # Fill in horizontal space
        hor_offset = int(room_hor_width / 2 - room_ver_width / 2)
        for y in range(0, room_ver_height):
            for x in range(hor_offset, room_ver_width + hor_offset):
                room[x][y] = 0

        return room

    def generateRandomVault(self):
        '''
        Parse vaults from Zorbus format into rooms
        Vault prefabs kindly provided by joonas@zorbus.net under the CC0 Creative Commons License:
        http://dungeon.zorbus.net/
        '''

        # 1. open random vault and trim empty lines
        vaults_path = 'resources/Zorbus_Vaults/Separate_files/'
        vault_filename = random.choice(os.listdir(vaults_path))
        vault_file = vaults_path + vault_filename
        with open(vault_file) as file:
            file_lines = file.readlines()
        # with open('resources/Zorbus_Vaults/Separate_files/sp_0118.txt') as file:
        #    file_lines = file.readlines()
        trimmed_file = [line for line in file_lines if line.strip()]

        # 2. check all rows and get trimmable whitespace, get room width and height
        trimmable_space = 0
        row_trimmable = 0
        vault_width = 0

        for row in trimmed_file:
            if trimmable_space == 0 or row_trimmable < trimmable_space:
                trimmable_space = row_trimmable
            row_empty_space_before_char = 0
            row_trimmable = 0
            row_characters_width = len(row.strip())
            if vault_width == 0 or row_characters_width > vault_width:
                vault_width = row_characters_width
            for tile in row:
                if tile == "#" or tile == ".":
                    row_trimmable = row_empty_space_before_char
                    break
                elif row_trimmable == 0:
                    row_empty_space_before_char += 1

        # make new room as array
        # loop all rows and trim shortest row length of characters from each
        # fill new array, replace whitespace with dashes until room width
        room = []

        for row in trimmed_file:
            new_room_row = []
            trimmed_row = row[trimmable_space:]
            for i in range(vault_width - 1):
                if i >= len(trimmed_row):
                    new_room_row.append(0)
                elif trimmed_row[i] == "#":
                    new_room_row.append(1)
                else:
                    new_room_row.append(0)
            room.append(new_room_row)

        return room

    def generateRoomSquare(self):
        roomWidth = random.randint(self.SQUARE_ROOM_MIN_SIZE, self.SQUARE_ROOM_MAX_SIZE)
        roomHeight = random.randint(max(int(roomWidth * 0.5), self.SQUARE_ROOM_MIN_SIZE),
                                    min(int(roomWidth * 1.5), self.SQUARE_ROOM_MAX_SIZE))

        room = [[0
                 for y in range(1, roomHeight - 1)]
                for x in range(1, roomWidth - 1)]

        return room

    def generateRoomCavern(self, max_size=18):
        while True:
            # if a room is too small, generate another
            room = [[1
                     for y in range(max_size)]
                    for x in range(max_size)]

            # random fill map
            for y in range(2, max_size - 2):
                for x in range(2, max_size - 2):
                    if random.random() >= self.wall_probability:
                        room[x][y] = 0

            # create distinctive regions
            for i in range(4):
                for y in range(1, max_size - 1):
                    for x in range(1, max_size - 1):

                        # if the cell's neighboring walls > self.neighbors, set it to 1
                        if self.get_adjacent_walls(x, y, room) > self.neighbors:
                            room[x][y] = 1
                        # otherwise, set it to 0
                        elif self.get_adjacent_walls(x, y, room) < self.neighbors:
                            room[x][y] = 0

            # flood_fill to remove small caverns
            room = self.flood_fill_remove(room)

            # start over if the room is completely filled in
            roomWidth, roomHeight = self.get_room_dimensions(room)
            for x in range(roomWidth):
                for y in range(roomHeight):
                    if room[x][y] == 0:
                        return room

    def flood_fill_remove(self, room):
        '''
        Find the largest region. Fill in all other regions.
        '''
        roomWidth, roomHeight = self.get_room_dimensions(room)
        largestRegion = set()

        for x in range(roomWidth):
            for y in range(roomHeight):
                if room[x][y] == 0:
                    newRegion = set()
                    tile = (x, y)
                    to_be_filled = set([tile])
                    while to_be_filled:
                        tile = to_be_filled.pop()

                        if tile not in newRegion:
                            newRegion.add(tile)

                            room[tile[0]][tile[1]] = 1

                            # check adjacent cells
                            x = tile[0]
                            y = tile[1]
                            north = (x, y - 1)
                            south = (x, y + 1)
                            east = (x + 1, y)
                            west = (x - 1, y)

                            for direction in [north, south, east, west]:

                                if room[direction[0]][direction[1]] == 0:
                                    if direction not in to_be_filled and direction not in newRegion:
                                        to_be_filled.add(direction)

                    if len(newRegion) >= self.ROOM_MIN_SIZE:
                        if len(newRegion) > len(largestRegion):
                            largestRegion.clear()
                            largestRegion.update(newRegion)

        for tile in largestRegion:
            room[tile[0]][tile[1]] = 0

        return room

    def placeRoom(self, room, map_width, map_height):  # (self,room,direction,)
        roomX = None
        roomY = None

        roomWidth, roomHeight = self.get_room_dimensions(room)

        # try n times to find a wall that lets you build room in that direction
        for i in range(self.placeRoomAttempts):
            # try to place the room against the tile, else connected by a tunnel of length i

            wallTile = None
            direction = self.getDirection()
            while not wallTile:
                '''
                randomly select tiles until you find
                a wall that has another wall in the
                chosen direction and has a floor in the 
                opposite direction.
                '''
                # direction == tuple(dx,dy)
                tile_x = random.randint(1, map_width - 2)
                tile_y = random.randint(1, map_height - 2)
                if ((self.level[tile_x][tile_y] == 1) and
                        (self.level[tile_x + direction[0]][tile_y + direction[1]] == 1) and
                        (self.level[tile_x - direction[0]][tile_y - direction[1]] == 0)):
                    wallTile = (tile_x, tile_y)

            # spawn the room touching wallTile
            startRoomX = None
            startRoomY = None
            '''
            TODO: replace this with a method that returns a 
            random floor tile instead of the top left floor tile
            '''
            while not startRoomX and not startRoomY:
                x = random.randint(0, roomWidth - 1)
                y = random.randint(0, roomHeight - 1)
                if room[x][y] == 0:
                    startRoomX = wallTile[0] - x
                    startRoomY = wallTile[1] - y

            # then slide it until it doesn't touch anything
            for tunnelLength in range(self.maxTunnelLength):
                possibleRoomX = startRoomX + direction[0] * tunnelLength
                possibleRoomY = startRoomY + direction[1] * tunnelLength

                enoughRoom = self.getOverlap(room, possibleRoomX, possibleRoomY, map_width, map_height)

                if enoughRoom:
                    roomX = possibleRoomX
                    roomY = possibleRoomY

                    # build connecting tunnel
                    # Attempt 1
                    '''
                    for i in range(tunnelLength+1):
                        x = wallTile[0] + direction[0]*i
                        y = wallTile[1] + direction[1]*i
                        self.level[x][y] = 0
                    '''
                    # moved tunnel code into self.generate_level()

                    return roomX, roomY, wallTile, direction, tunnelLength

        return None, None, None, None, None

    def addRoom(self, roomX, roomY, room):
        roomWidth, roomHeight = self.get_room_dimensions(room)
        level_size_y = len(self.level)
        level_size_x = len(self.level[0])

        for x in range(roomWidth):
            for y in range(roomHeight):
                if int(roomY + y) > level_size_y or int(roomX + x) > level_size_x:
                    continue
                if room[x][y] == 0:
                    self.level[int(roomX + x)][int(roomY + y)] = 0


        self.rooms_list.append(room)

    def addTunnel(self, wallTile, direction, tunnelLength):
        # carve a tunnel from a point in the room back to
        # the wall tile that was used in its original placement

        startX = wallTile[0] + direction[0] * tunnelLength
        startY = wallTile[1] + direction[1] * tunnelLength
        # self.level[startX][startY] = 1

        for i in range(self.maxTunnelLength):
            x = startX - direction[0] * i
            y = startY - direction[1] * i
            self.level[x][y] = 0
            # If you want doors, this is where the code should go
            if ((x + direction[0]) == wallTile[0] and
                    (y + direction[1]) == wallTile[1]):
                break

    def get_room_dimensions(self, room):
        if room:
            roomWidth = len(room)
            roomHeight = len(room[0])
            return roomWidth, roomHeight
        else:
            roomWidth = 0
            roomHeight = 0
            return roomWidth, roomHeight

    def getDirection(self):
        # direction = (dx,dy)
        north = (0, -1)
        south = (0, 1)
        east = (1, 0)
        west = (-1, 0)

        direction = random.choice([north, south, east, west])
        return direction

    def getOverlap(self, room, roomX, roomY, map_width, map_height):
        '''
        for each 0 in room, check the cooresponding tile in
        self.level and the eight tiles around it. Though slow,
        that should insure that there is a wall between each of
        the rooms created in this way.
        <> check for overlap with self.level
        <> check for out of bounds
        '''
        roomWidth, roomHeight = self.get_room_dimensions(room)
        for x in range(roomWidth):
            for y in range(roomHeight):
                if room[x][y] == 0:
                    # Check to see if the room is out of bounds
                    if ((1 <= (x + roomX) < map_width - 1) and
                            (1 <= (y + roomY) < map_height - 1)):
                        # Check for overlap with a one tile buffer
                        if self.level[x + roomX - 1][y + roomY - 1] == 0:  # top left
                            return False
                        if self.level[x + roomX][y + roomY - 1] == 0:  # top center
                            return False
                        if self.level[x + roomX + 1][y + roomY - 1] == 0:  # top right
                            return False

                        if self.level[x + roomX - 1][y + roomY] == 0:  # left
                            return False
                        if self.level[x + roomX][y + roomY] == 0:  # center
                            return False
                        if self.level[x + roomX + 1][y + roomY] == 0:  # right
                            return False

                        if self.level[x + roomX - 1][y + roomY + 1] == 0:  # bottom left
                            return False
                        if self.level[x + roomX][y + roomY + 1] == 0:  # bottom center
                            return False
                        if self.level[x + roomX + 1][y + roomY + 1] == 0:  # bottom right
                            return False

                    else:  # room is out of bounds
                        return False
        return True

    def addShortcuts(self, map_width, map_height):
        '''
        I use libtcodpypy's built in pathfinding here, since I'm
        already using libtcodpypy for the iu. At the moment,
        the way I find the distance between
        two points to see if I should put a shortcut there
        is horrible, and its easily the slowest part of this
        algorithm. If I think of a better way to do this in
        the future, I'll implement it.
        '''

        # initialize the libtcodpypy map
        libtcodpyMap = tcod_map.Map(map_width, map_height)
        self.recomputePathMap(map_width, map_height, libtcodpyMap)

        for i in range(self.shortcutAttempts):
            # check i times for places where shortcuts can be made
            while True:
                # Pick a random floor tile
                floorX = random.randint(self.shortcutLength + 1, (map_width - self.shortcutLength - 1))
                floorY = random.randint(self.shortcutLength + 1, (map_height - self.shortcutLength - 1))
                if self.level[floorX][floorY] == 0:
                    if (self.level[floorX - 1][floorY] == 1 or
                            self.level[floorX + 1][floorY] == 1 or
                            self.level[floorX][floorY - 1] == 1 or
                            self.level[floorX][floorY + 1] == 1):
                        break

            # look around the tile for other floor tiles
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x != 0 or y != 0:  # Exclude the center tile
                        newX = floorX + (x * self.shortcutLength)
                        newY = floorY + (y * self.shortcutLength)
                        if self.level[newX][newY] == 0:
                            # run pathfinding algorithm between the two points
                            # back to the libtcodpypy nonesense
                            pathMap = libtcodpy.path_new_using_map(libtcodpyMap)
                            libtcodpy.path_compute(pathMap, floorX, floorY, newX, newY)
                            distance = libtcodpy.path_size(pathMap)

                            if distance > self.minPathfindingDistance:
                                # make shortcut
                                self.carveShortcut(floorX, floorY, newX, newY)
                                self.recomputePathMap(map_width, map_height, libtcodpyMap)

        # destroy the path object
        libtcodpy.path_delete(pathMap)

    def recomputePathMap(self, map_width, map_height, libtcodpyMap):
        for x in range(map_width):
            for y in range(map_height):
                if self.level[x][y] == 1:
                    # libtcodpy.map_set_properties(libtcodpyMap, x, y, False, False)
                    libtcodpyMap.walkable[y][x] = False
                    libtcodpyMap.transparent[y][x] = False
                else:
                    libtcodpyMap.walkable[y][x] = True
                    libtcodpyMap.transparent[y][x] = True
                    # libtcodpy.map_set_properties(libtcodpyMap, x, y, True, True)

    def carveShortcut(self, x1, y1, x2, y2):
        if x1 - x2 == 0:
            # Carve virtical tunnel
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.level[x1][y] = 0

        elif y1 - y2 == 0:
            # Carve Horizontal tunnel
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.level[x][y1] = 0

        elif (y1 - y2) / (x1 - x2) == 1:
            # Carve NW to SE Tunnel
            x = min(x1, x2)
            y = min(y1, y2)
            while x != max(x1, x2):
                x += 1
                self.level[x][y] = 0
                y += 1
                self.level[x][y] = 0

        elif (y1 - y2) / (x1 - x2) == -1:
            # Carve NE to SW Tunnel
            x = min(x1, x2)
            y = max(y1, y2)
            while x != max(x1, x2):
                x += 1
                self.level[x][y] = 0
                y -= 1
                self.level[x][y] = 0

    def checkRoomExists(self, room):
        roomWidth, roomHeight = self.get_room_dimensions(room)
        for x in range(roomWidth):
            for y in range(roomHeight):
                if room[x][y] == 0:
                    return True
        return False

    def get_caves(self):
        # locate all the caves within self.level and store them in self.rooms
        for x in range(0, self.map_width):
            for y in range(0, self.map_height):
                if self.level[x][y] == 0:
                    self.flood_fill(x, y)

        for room in self.rooms:
            cave = room.cave
            for tile in cave:
                self.level[tile[0]][tile[1]] = 0

    def flood_fill(self, x, y):
        '''
        flood fill the separate regions of the level, discard
        the regions that are smaller than a minimum size, and
        create a reference for the rest.
        '''
        cave = set()
        tile = (x, y)
        to_be_filled = {tile}
        while to_be_filled:
            tile = to_be_filled.pop()

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
                        if direction not in to_be_filled and direction not in cave:
                            to_be_filled.add(direction)

        if self.ROOM_MIN_SIZE <= len(cave) <= 300:

            x1 = min(cave, key=lambda t: t[0])[0]
            x2 = max(cave, key=lambda t: t[0])[0]
            y1 = min(cave, key=lambda t: t[1])[1]
            y2 = max(cave, key=lambda t: t[1])[1]
            w = x2 - x1
            h = y2 - y1
            id_nr = len(self.rooms) + 1

            room = Room(x1=x1, y1=y1, x2=x2, y2=y2, w=w, h=h, cave=cave, id_nr=id_nr)
            self.rooms.append(room)

    def connect_caves(self):
        # Find the closest cave to the current cave
        for current_cave_room in self.rooms:
            current_cave = current_cave_room.cave
            for point1 in current_cave:
                break  # get an element from cave1
            point2 = None
            distance = None
            for next_cave_room in self.rooms:
                next_cave = next_cave_room.cave
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
                self.create_tunnel(point1, point2, current_cave)

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

                    if self.level[direction[0]][direction[1]] == 0:
                        if direction not in to_be_filled and direction not in connected_region:
                            to_be_filled.add(direction)

        for end in cave2:
            break  # get an element from cave2

        if end in connected_region:
            return True

        else:
            return False

    def create_tunnel(self, point1, point2, current_cave):
        # run a heavily weighted random Walk
        # from point1 to point1
        drunkard_x = point2[0]
        drunkard_y = point2[1]
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
                if self.level[drunkard_x][drunkard_y] == 1:
                    self.level[drunkard_x][drunkard_y] = 0
