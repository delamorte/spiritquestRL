import os
import random

from map_gen.dungeon import Dungeon


# ==== Room Addition ====
class RoomAddition(Dungeon):
    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.rooms = []
        self.rooms_list = []
        self.level = []

        self.ROOM_MAX_SIZE = 18  # max height and width for cellular automata rooms
        self.ROOM_MIN_SIZE = 16  # min size in number of floor tiles, not height and width
        self.MAX_NUM_ROOMS = 20

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

        self.buildRoomAttempts = 400
        self.placeRoomAttempts = 10
        self.maxTunnelLength = 20

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
        roomWidth, roomHeight = self.map_width, self.map_height
        while roomWidth >= self.map_width or roomHeight >= self.map_height:
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
                if len(self.rooms_list) >= self.MAX_NUM_ROOMS:
                    break

        self.get_caves()
        self.connect_caves()
        self.clean_up_map(self.map_width, self.map_height)
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
                    if ((1 <= (x + 1 + roomX) < map_width - 1) and
                            (1 <= (y + 1 + roomY) < map_height - 1)):
                        # Check for overlap with a one tile buffer
                        if self.level[x + roomX - 1][y + roomY - 1] == 0 or self.level[x + roomX - 2][y + roomY - 2] == 0:  # top left
                            return False
                        if self.level[x + roomX][y + roomY - 1] == 0 or self.level[x + roomX][y + roomY - 2] == 0:  # top center
                            return False
                        if self.level[x + roomX + 1][y + roomY - 1] == 0 or self.level[x + roomX + 2][y + roomY - 2] == 0:  # top right
                            return False

                        if self.level[x + roomX - 1][y + roomY] == 0 or self.level[x + roomX - 2][y + roomY] == 0:  # left
                            return False
                        if self.level[x + roomX][y + roomY] == 0:  # center
                            return False
                        if self.level[x + roomX + 1][y + roomY] == 0 or self.level[x + roomX + 2][y + roomY] == 0:  # right
                            return False

                        if self.level[x + roomX - 1][y + roomY + 1] == 0 or self.level[x + roomX - 2][y + roomY + 2] == 0:  # bottom left
                            return False
                        if self.level[x + roomX][y + roomY + 1] == 0 or self.level[x + roomX][y + roomY + 2] == 0:  # bottom center
                            return False
                        if self.level[x + roomX + 1][y + roomY + 1] == 0 or self.level[x + roomX + 2][y + roomY + 2] == 0:  # bottom right
                            return False

                    else:  # room is out of bounds
                        return False
        return True
