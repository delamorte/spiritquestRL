# ==== Tunneling Algorithm ====
import random

from map_gen.dungeon import Room, Dungeon


class TunnelingAlgorithm(Dungeon):
    '''
    This version of the tunneling algorithm is essentially
    identical to the tunneling algorithm in the Complete Roguelike
    Tutorial using Python, which can be found at
    http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcodpy,_part_1

    Requires random.randint() and the Rect class defined below.
    '''

    def __init__(self, map_width=None, map_height=None):
        super().__init__(map_width=map_width, map_height=map_height)
        self.level = []
        self.ROOM_MAX_SIZE = 15
        self.ROOM_MIN_SIZE = 6
        self.MAX_ROOMS = 30
        # TODO: raise an error if any necessary classes are missing

    def generate_level(self, map_width, map_height):
        # Creates an empty 2D array or clears existing array
        self.level = [[1 for y in range(map_height)]
                      for x in range(map_width)]

        rooms = []
        num_rooms = 0

        for r in range(self.MAX_ROOMS):
            # random width and height
            w = random.randint(self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            h = random.randint(self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            # random position within map boundries
            x = random.randint(0, map_width - w - 1)
            y = random.randint(0, map_height - h - 1)

            new_room = Room(x, y, w, h)
            # check for overlap with previous rooms
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room_rect(new_room)
                (new_x, new_y) = new_room.get_center()

                if num_rooms != 0:
                    # all rooms after the first one
                    # connect to the previous room

                    # center coordinates of the previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].get_center()

                    # 50% chance that a tunnel will start horizontally
                    if random.randint(0, 1) == 1:
                        self.createHorTunnel(prev_x, new_x, prev_y)
                        self.createVirTunnel(prev_y, new_y, new_x)

                    else:  # else it starts virtically
                        self.createVirTunnel(prev_y, new_y, prev_x)
                        self.createHorTunnel(prev_x, new_x, new_y)

                # append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        return self.level

    def createHorTunnel(self, x1, x2, y):
        y = int(y)
        for x in range(int(min(x1, x2)), int(max(x1, x2) + 1)):
            self.level[x][y] = 0

    def createVirTunnel(self, y1, y2, x):
        x = int(x)
        for y in range(int(min(y1, y2)), int(max(y1, y2) + 1)):
            self.level[x][y] = 0
