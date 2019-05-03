from components.item import Item
from entity import Entity
from fighter_stats import get_fighter_stats, get_fighter_ai
from map_objects.tile import Tile
from map_objects.tilemap import tilemap
from random import randint
from components.stairs import Stairs
from components.door import Door

class GameMap:
    def __init__(self, width, height, name, dungeon_level=0):
        self.width = width
        self.height = height
        self.name = name
        self.dungeon_level = dungeon_level
        self.rooms = {}
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):

        tiles = [[Tile(False, False, x, y)
                  for y in range(self.height)]
                 for x in range(self.width)]

        # Block edges of map
        for y in range(self.height):
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or
                        y == 0 or y == self.height - 1):
                    tiles[x][y].blocked = True
                    tiles[x][y].block_sight = True

        return tiles

    def create_room(self, room):

        for y in range(room.y1, room.y2):
            for x in range(room.x1, room.x2):
                self.tiles[x][y].occupied = True
                if (x == room.x1 or x == room.x2 - 1 or
                        y == room.y1 or y == room.y2 - 1):
                    self.tiles[x][y].color[1] = room.wall_color
                    self.tiles[x][y].char[1] = room.wall
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
                else:
                    self.tiles[x][y].color[0] = room.floor_color
                    self.tiles[x][y].char[0] = tilemap()["floor"][0]
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False
                    self.tiles[x][y].spawnable = True
        
        # Make sure nothing can block room wall immediate neighbours            
        for y in range(room.y1-1, room.y2+1):
            for x in range(room.x1-1, room.x2+1):
                self.tiles[x][y].occupied = True
        
        # Add special (named) rooms to a list so they can be called later
        if room.name:
            self.rooms[room.name] = room

    def count_walls(self, n, x, y):
        wall_count = 0

        for r in range(-n, n + 1):
            for c in range(-n, n + 1):
                if x + r >= self.width or x + r <= 0 or y + c >= self.height or y + c <= 0:
                    wall_count += 1
                elif self.tiles[x + r][y + c].blocked:
                    wall_count += 1

        return wall_count

    def generate_hub(self):

        # Set ground tiles
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                self.tiles[x][y].color[0] = "dark amber"
                self.tiles[x][y].char[0] = tilemap()["ground_soil"][randint(
                    0, (len(tilemap()["ground_soil"]) - 1))]

        # Generate a house
        w = 10
        h = 10
        x1 = randint(2, self.width - w - 2)
        y1 = randint(2, self.height - h - 2)

        home = Room(x1, y1, 10, 10, tilemap()[
                    "wall_brick"], "orange", "dark gray", "home")

        self.create_room(home)
        door_home = home.create_door(self, "open")

        # Generate dungeon entrance
        w = 10
        h = 10
        x1 = randint(2, self.width - w - 2)
        y1 = randint(2, self.height - h - 2)
        x2 = x1 + w
        y2 = y1 + h

        # Make sure room doesn't overlap with existing rooms
        while (self.tiles[x1][y1].occupied or
               self.tiles[x2][y2].occupied or
               self.tiles[x2][y1].occupied or
               self.tiles[x1][y2].occupied):
            x1 = randint(1, self.width - w - 1)
            y1 = randint(1, self.height - h - 1)
            x2 = x1 + w
            y2 = y1 + h

        d_entrance = Room(x1, y1, 10, 10, tilemap()["wall_brick"], "dark amber", "darkest amber", "d_entrance")

        self.create_room(d_entrance)
        door_d_entrance = d_entrance.create_door(self, "locked")

        walls = d_entrance.get_walls()
        for i in walls:
            wall_to_moss = randint(0, len(d_entrance.get_walls()) - 1)
            x, y = i
            if wall_to_moss < len(d_entrance.get_walls()) / 2 and not self.tiles[x][y].char[1] in tilemap()["door"].values():

                self.tiles[x][y].char[1] = tilemap()["wall_moss"][randint(
                    0, (len(tilemap()["wall_moss"]) - 1))]
        
        self.generate_trees(1, 1, self.width-1, self.height-1,
                    20, block_sight=True)

        # Create starting weapon in hub
        x, y = self.rooms["home"].get_center()
        item_component = Item()
        weapon = Entity(x + 2, y + 2, 11, tilemap()
                        ["weapons"]["club"], None, "club", item=item_component)

        center_x, center_y = self.rooms["home"].get_center()
        stairs_component = Stairs(("hub", center_x, center_y), ["dream"])
        campfire = Entity(center_x, center_y, 2, tilemap()["campfire"], "lightest orange", "campfire", stairs=stairs_component)
        campfire.xtra_info = "Meditate and go to dream world with '<' or '>'"
        
        center_x, center_y = self.rooms["d_entrance"].get_center()
        
        stairs_component = Stairs(("hub", center_x, center_y), ["cavern1"], "stairs down", 0)
        stairs_down = Entity(center_x, center_y, 2, tilemap()["stairs"]["down"], "dark amber", "stairs to a mysterious cavern", stairs=stairs_component)
        stairs_down.xtra_info = "You feel an ominous presence. Go down with '<' or '>'"
        
        entities={}
        entities["items"] = [weapon]
        entities["stairs"] = [campfire, stairs_down]
        entities["doors"] = [door_home, door_d_entrance]
        return entities

    def generate_forest(self):
        
        entities={}
        cavern_colors = ["lightest amber",
                         "lighter amber",
                         "light amber",
                         "dark amber",
                         "darker amber",
                         "darkest amber"]

        for y in range(1, self.height-1):
            for x in range(1, self.width-1):

                self.tiles[x][y].color[0] = cavern_colors[3]
                self.tiles[x][y].char[0] = tilemap()["ground_soil"][randint(
                    0, (len(tilemap()["ground_soil"]) - 1))]
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                self.tiles[x][y].spawnable = True

        for i in range(self.width):
            dx = randint(1, self.width - 1)
            dy = randint(1, self.height - 1)
            width = dx + randint(5, self.width / 5)
            if width > self.width:
                width = self.width
            height = dy + randint(5, self.width / 5)
            if height > self.height:
                height = self.height
            freq = randint(10, 40)
            block_sight = True
            self.generate_trees(dx, dy, width, height, freq, block_sight)

        # Generate rocks & rubble on floor tiles
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.is_blocked(x, y):
                    if randint(1, 4) >= self.tiles[x][y].seed:
                        self.tiles[x][y].color[1] = "dark gray"
                        self.tiles[x][y].char[1] = tilemap()["rubble"][randint(
                            0, (len(tilemap()["rubble"]) - 1))]
        return entities

    def generate_trees(self, dx, dy, width, height, freq, block_sight):
        """Generate a forest to a rectangular area."""

        forest_colors = ["lightest orange",
                         "lighter orange",
                         "light orange",
                         "dark orange",
                         "darker orange"]

        for y in range(dy, height):
            for x in range(dx, width):
                if not self.tiles[x][y].occupied:
                    self.tiles[x][y].color[0] = "dark amber"
                    self.tiles[x][y].char[0] = tilemap()["ground_soil"][randint(
                        0, (len(tilemap()["ground_soil"]) - 1))]
                    self.tiles[x][y].spawnable = False
    
                    # Generate forest tiles
                    if randint(0, 100) < freq:
                        self.tiles[x][y].char[1] = tilemap()["tree"][randint(
                            0, (len(tilemap()["tree"]) - 1))]
                        self.tiles[x][y].color[1] = forest_colors[randint(0, 4)]
                        self.tiles[x][y].blocked = True
                        self.tiles[x][y].block_sight = block_sight

    def generate_cavern(self, entities):

        cavern_colors = ["lightest amber",
                         "lighter amber",
                         "light amber",
                         "dark amber",
                         "darker amber",
                         "darkest amber"]

        for y in range(self.height):
            for x in range(self.width):

                self.tiles[x][y].color[0] = cavern_colors[4]
                self.tiles[x][y].char[0] = tilemap()["ground_moss"][randint(
                    0, (len(tilemap()["ground_moss"]) - 1))]
                self.tiles[x][y].visited = False
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                freq = randint(1, 100)
                if freq < 50:
                    self.tiles[x][y].color[1] = cavern_colors[4]
                    self.tiles[x][y].char[1] = tilemap()["wall_moss"][randint(
                        0, (len(tilemap()["wall_moss"]) - 1))]
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True

        for i in range(5):
            for x in range(self.width):
                for y in range(self.height):
                    wall_one_away = self.count_walls(1, x, y)
                    wall_two_away = self.count_walls(2, x, y)

                    if wall_one_away >= 5 or wall_two_away <= 2:
                        self.tiles[x][y].color[1] = cavern_colors[4]
                        self.tiles[x][y].char[1] = tilemap()["wall_moss"][randint(
                            0, (len(tilemap()["wall_moss"]) - 1))]
                        self.tiles[x][y].blocked = True
                        self.tiles[x][y].block_sight = True

                    else:
                        self.tiles[x][y].blocked = False
                        self.tiles[x][y].block_sight = False
                        self.tiles[x][y].char[1] = " "

        # Smooth out singular walls in empty spaces

        #=======================================================================
        # for i in range (5):
        #     for x in range (self.width):
        #         for y in range (self.height):
        #             wall_one_away = self.count_walls(1, x, y)
        # 
        #             if wall_one_away >= 5:
        #                 self.tiles[x][y].color[1] = cavern_colors[4]
        #                 self.tiles[x][y].char[1] = tilemap()["wall_moss"][randint(
        #                     0, (len(tilemap()["wall_moss"]) - 1))]
        #                 self.tiles[x][y].blocked = True
        #                 self.tiles[x][y].block_sight = False
        #             else:
        #                 self.tiles[x][y].blocked = False
        #                 self.tiles[x][y].block_sight = False
        #                 self.tiles[x][y].char[1] = " "
        #=======================================================================


        for y in range(self.height):
            for x in range(self.width):
                wall_one_away = self.count_walls(1, x, y)
                    
                if (x == 1 or x == self.width - 2 or
                        y == 1 or y == self.height - 2):
                    self.tiles[x][y].color[1] = cavern_colors[4]
                    self.tiles[x][y].char[1] = tilemap()["wall_moss"][randint(
                        0, (len(tilemap()["wall_moss"]) - 1))]
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
                

        cavern = []
        total_cavern_area = []
        caverns = []

        for x in range(0, self.width - 1):
            for y in range(0, self.height - 1):
                tile = self.tiles[x][y]

                if not tile.visited and not tile.blocked:
                    cavern.append(self.tiles[x][y])

                    while len(cavern) > 0:

                        node = cavern[len(cavern) - 1]
                        cavern = cavern[:len(cavern) - 1]

                        if not node.visited and not node.blocked:
                            node.visited = True
                            total_cavern_area.append(node)

                            if node.x - 1 > 0 and not self.tiles[node.x - 1][node.y].blocked:
                                cavern.append(self.tiles[node.x - 1][node.y])

                            if node.x + 1 < self.width and not self.tiles[node.x + 1][node.y].blocked:
                                cavern.append(self.tiles[node.x + 1][node.y])

                            if node.y - 1 > 0 and not self.tiles[node.x][node.y - 1].blocked:
                                cavern.append(self.tiles[node.x][node.y - 1])

                            if node.y + 1 < self.height and not self.tiles[node.x][node.y + 1].blocked:
                                cavern.append(self.tiles[node.x][node.y + 1])

                    caverns.append(total_cavern_area)
                    total_cavern_area = []

                else:
                    tile.visited = True
        
        # Set the largest cavern as main cave and fill out the rest
        caverns.sort(key=len)
        main_cave = caverns[len(caverns) - 1]
        caverns = caverns[:len(caverns)-1]
        
        for i in range(0, len(caverns)):
            for j in range (0, len(caverns[i])):
                caverns[i][j].color[1] = cavern_colors[4]
                caverns[i][j].char[1] = tilemap()["wall_moss"][randint(
                    0, (len(tilemap()["wall_moss"]) - 1))]
                caverns[i][j].blocked = True
                caverns[i][j].block_sight = True

        # Get random position in the main cave
        pos = randint(0, len(main_cave)-1)
        px, py = main_cave[pos].x, main_cave[pos].y

        stairs_current_floor = []
        # On the first floor there is only one set of stairs up which leads back to hub        
        if self.dungeon_level == 1:
            stairs_component = Stairs(("cavern1", px, py),["hub", entities["stairs"][1].stairs.source[1], entities["stairs"][1].stairs.source[2]], "hub", self.dungeon_level)
            entities["stairs"][1].stairs.destination.extend((px, py))
            stairs_up = Entity(px, py, 1, tilemap()["stairs"]["up"], "dark amber","stairs up", stairs=stairs_component)
            stairs_current_floor.append(stairs_up)
        # Make as many stairs upstairs as previous floor had stairs down
        else:
            for i, entity in enumerate(entities["stairs"]):
                if entity.stairs.name == "stairs down":
                    pos = randint(0, len(main_cave)-1)
                    px, py = main_cave[pos].x, main_cave[pos].y
                    stairs_component = Stairs(("cavern"+str(self.dungeon_level), px, py), ["cavern"+str(self.dungeon_level-1), entity.stairs.source[1], entity.stairs.source[2]], "stairs up", self.dungeon_level)
                    stairs_up = Entity(px, py, 1, tilemap()["stairs"]["up"], "dark amber","stairs up", stairs=stairs_component)
                    # Connect the stairs with previous level's down going stairs
                    entity.stairs.destination.extend((px, py))
                    stairs_current_floor.append(stairs_up)
        
        entities = {}
        
        # Create 3 sets of stairs down
        for i in range (1,4):        
            pos = randint(0, len(main_cave)-1)
            px, py = main_cave[pos].x, main_cave[pos].y
            stairs_component = Stairs(("cavern"+str(self.dungeon_level), px, py),["cavern"+str(self.dungeon_level + 1)], "stairs down", self.dungeon_level)
            stairs_down = Entity(px, py, 2, tilemap()["stairs"]["down"], "dark amber","stairs down", stairs=stairs_component)
            stairs_current_floor.append(stairs_down)
        
        entities["stairs"] = []    
        for entity in stairs_current_floor:
            entities["stairs"].append(entity)
        
        return entities
    
    def is_blocked(self, x, y):

        if x >= self.width-1 or x <= 0 or y >= self.height-1 or y <= 0:
            return True
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, player, entities, stairs=None):
        
        if self.name == "hub":
            center_x, center_y = self.rooms["home"].get_center()
            player.x, player.y = center_x - 1, center_y - 1

        if self.name == "dream":
            px, py = randint(1, self.width - 1), \
                randint(1, self.height - 1)
    
            while not self.tiles[px][py].spawnable:
                
        #    while self.is_blocked(px, py):
                px, py = randint(1, self.width - 1), \
                    randint(1, self.height - 1)
            player.x, player.y = px, py
            
        if stairs:
            player.x, player.y = stairs.destination[1], stairs.destination[2]

        # Player spawning point has been set in all scenarios, now place rest of the entities
        entities["player"] = [player]
        entities["monsters"] = []
        
        if self.name == "debug":
            player.x, player.y = 2, 2
            number_of_monsters = 0
            monsters = []
            for x, y in tilemap()["monsters"].items():
                if x == "rat":
                    monsters.append((x, y))
            
            for i in range(number_of_monsters):
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y):
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)
            
                if not any([entity for entity in entities["monsters"] if entity.x == x and entity.y == y]):
                    #r = randint(0, 2)
                    name, char = monsters[0]
                    fighter_component = get_fighter_stats(name)
                    ai_component = get_fighter_ai(name)
                    monster = Entity(x, y, 12, char,
                                     None, name, blocks=True, fighter=fighter_component, ai=ai_component)
                    entities["monsters"].append(monster)
   
        if stairs and self.name == "cavern"+str(stairs.floor+1):
        
            number_of_monsters = randint(self.width / 2 - 40, self.width / 2 - 20)
            #number_of_monsters = 0
            monsters = []
            for x, y in tilemap()["monsters"].items():
                if x == "frog":
                    monsters.append((x, y))
            
            for i in range(number_of_monsters):
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y):
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)
            
                if not any([entity for entity in entities["monsters"] if entity.x == x and entity.y == y]):
                    #r = randint(0, 2)
                    name, char = monsters[0]
                    fighter_component = get_fighter_stats(name)
                    ai_component = get_fighter_ai(name)
                    monster = Entity(x, y, 12, char,
                                     None, name, blocks=True, fighter=fighter_component, ai=ai_component)
                    entities["monsters"].append(monster)     

        if self.name is "dream":
            
            number_of_monsters = randint(self.width / 2 - 20, self.width / 2)
            monsters = []
            for x, y in tilemap()["monsters"].items():
                monsters.append((x, y))

            for i in range(number_of_monsters):
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y):
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)

                if not any([entity for entity in entities["monsters"] if entity.x == x and entity.y == y]):
                    r = randint(0, 2)
                    name, char = monsters[r]
                    fighter_component = get_fighter_stats(name)
                    ai_component = get_fighter_ai(name)
                    monster = Entity(x, y, 12, char,
                                     None, name, blocks=True, fighter=fighter_component, ai=ai_component)
                    entities["monsters"].append(monster)

        return player, entities
    
class Room ():
    def __init__(self, x1, y1, w, h, wall, wall_color, floor_color, name=None):
        self.x1 = x1
        self.y1 = y1
        self.w = w
        self.h = h
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h
        self.wall = wall
        self.wall_color = wall_color
        self.floor_color = floor_color
        self.name = name

    def get_room_tiles(self):

        area = []

        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                area.append((x, y))

        return area

    def get_walls(self):

        walls = []

        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                if (x == self.x1 or x == self.x2 - 1 or
                        y == self.y1 or y == self.y2 - 1):
                    walls.append((x, y))

        return walls

    def get_center(self):

        center_x = int((self.x1 + self.x1 + self.w) / 2)
        center_y = int((self.y1 + self.y1 + self.h) / 2)

        return center_x, center_y
    
    def create_door(self, parent, status):
        
        """
        Generate one door at a random position in the room.
        If any of the room walls are against the map border,
        make sure that door cannot be placed there.
        """
        
        door_seed = randint(0, len(self.get_walls()) - 1)

        walls = self.get_walls()

        while walls[door_seed][0] == 1 or walls[door_seed][0] == self.w - 1 or walls[door_seed][1] == 1 or walls[door_seed][1] == self.h - 1:
            door_seed = randint(0, len(self.get_walls()) - 1)
        
        door_component = Door(self.name, status)
        door = Entity(walls[door_seed][0], walls[door_seed][1], 2, tilemap()["door"][status], None, "door", door=door_component)
        
        if status == "open":
            parent.tiles[walls[door_seed][0]][walls[door_seed][1]].blocked = False
            parent.tiles[walls[door_seed][0]][walls[door_seed][1]].block_sight = False
        else:
            parent.tiles[walls[door_seed][0]][walls[door_seed][1]].blocked = True
            parent.tiles[walls[door_seed][0]][walls[door_seed][1]].block_sight = True
            
        return door

