from components.item import Item
from entity import Entity
from fighter_stats import get_fighter_stats, get_fighter_ai, get_spawn_rates
from helpers import flatten
from map_objects.tile import Tile
from map_objects.tilemap import tilemap, openables, items, stairs
from palettes import get_dngn_colors, get_forest_colors, get_monster_color, name_color_from_value, get_terrain_colors
from random import choices, randint
from components.stairs import Stairs
from components.door import Door
from components.wall import Wall
from components.light_source import LightSource
from resources.dungeon_generation.dungeon_generator import DrunkardsWalk
from resources.dungeon_generation.dungeon_generator import RoomAddition
import xml.etree.ElementTree as ET
import variables
import numpy as np


class GameMap:
    def __init__(self, width, height, name, dungeon_level=0):
        self.width = width
        self.height = height
        self.name = name
        self.dungeon_level = dungeon_level
        self.rooms = {}
        self.tiles = self.initialize_tiles()
        self.drunkardsWalk = DrunkardsWalk()
        self.roomAddition = RoomAddition()

    def initialize_tiles(self):

        tiles = np.array([[Tile(False, False, x, y)
                  for y in range(self.height)]
                 for x in range(self.width)])

        # Block edges of map
        for y in range(self.height):
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or
                        y == 0 or y == self.height - 1):
                    tiles[x][y].blocked = True
                    tiles[x][y].block_sight = True

        return tiles

    def create_room(self, room):
        entities = []
        for y in range(room.y1, room.y2):
            for x in range(room.x1, room.x2):
                self.tiles[x][y].occupied = True
                self.tiles[x][y].natural_light_level = room.lightness

                if room.tiled:
                    ground = room.layers[0][y - room.y1][x - room.x1]
                    ground_top = room.layers[1][y - room.y1][x - room.x1]
                    entity = room.layers[2][y - room.y1][x - room.x1]

                    if ground != 0:
                        name, color = name_color_from_value(ground)
                        if variables.gfx == "oryx":
                            ground += 0xE500
                        else:
                            ground = tilemap()[name]
                        self.tiles[x][y].char = ground
                        if color is not None:
                            self.tiles[x][y].color = color

                    if ground_top != 0:
                        name, color = name_color_from_value(ground_top)
                        if variables.gfx == "oryx":
                            ground_top += 0xE500
                        else:
                            ground_top = tilemap()[name]
                        self.tiles[x][y].layers.append((ground_top, color))

                    if entity != 0:
                        name, color = name_color_from_value(entity)
                        if variables.gfx == "oryx":
                            entity += 0xE500
                        else:
                            if isinstance(tilemap()[name], tuple):
                                entity = tilemap()[name][0]
                            else:
                                entity = tilemap()[name]

                        if "," in name:
                            name = name.split(",")[0]
                        if name in openables:
                            door_component = Door(name)
                            door = Entity(x, y, 2, entity,
                                          color, name, door=door_component, stand_on_messages=False)
                            self.tiles[x][y].entities_on_tile.append(door)
                            door_component.set_status(door_component.status, self)
                            entities.append(door)
                        elif name in items:
                            item_component = Item(name)
                            item = Entity(x, y, 2, entity,
                                          color, name, item=item_component)
                            self.tiles[x][y].entities_on_tile.append(item)
                            item_component.set_attributes(self)
                            entities.append(item)
                        elif name in stairs:
                            stairs_component = Stairs(("hub", x, y), ["dream"], name)
                            portal = Entity(x, y, 1, entity, color, name,
                                                stairs=stairs_component)
                            self.tiles[x][y].entities_on_tile.append(portal)
                            stairs_component.set_attributes(self)
                            portal.xtra_info = "Meditate and go to dream world with '<' or '>'"
                            entities.append(portal)
                        else:
                            wall_component = Wall(name)
                            wall = Entity(x, y, 2, entity,
                                          color, name, wall=wall_component)
                            self.tiles[x][y].entities_on_tile.append(wall)
                            wall_component.set_attributes(self)
                            entities.append(wall)

                else:
                    # Vertical walls
                    if (x == room.x1 or x == room.x2 - 1) and 0 <= y < room.y2 - 1:
                        wall_component = Wall(room.wall)
                        wall = Entity(x, y, 2, tilemap()[room.wall]["vertical"],
                                      room.wall_color, room.wall, wall=wall_component)
                        self.tiles[x][y].entities_on_tile.append(wall)
                        wall_component.set_attributes(self)
                        entities.append(wall)

                    # Horizontal walls
                    elif (y == room.y1 or y == room.y2 - 1) and 0 <= x <= room.x2 - 1:
                        wall_component = Wall(room.wall)
                        wall = Entity(x, y, 2, tilemap()[room.wall]["horizontal"],
                                      room.wall_color, room.wall, wall=wall_component)
                        self.tiles[x][y].entities_on_tile.append(wall)
                        wall_component.set_attributes(self)
                        entities.append(wall)

                    #                 # Upper left corner
                    #                 elif x == room.x1 and y == room.y1:
                    #                     pass
                    #                 # Upper right corner
                    #                 elif x == room.x2 and y == room.y1:
                    #                     pass
                    #                 # Lower left corner
                    #                 elif x == room.x1 and y == room.y2:
                    #                     pass
                    #                 # Lower right corner
                    #                 elif x == room.x2 and y == room.y2:
                    #                     pass

                    else:
                        self.tiles[x][y].color = room.floor_color
                        self.tiles[x][y].char = tilemap()[room.floor]
                        #                     self.tiles[x][y].blocked = False
                        #                     self.tiles[x][y].block_sight = False
                        self.tiles[x][y].spawnable = True

        # Make sure nothing can block room wall immediate neighbours
        for y in range(room.y1 - 1, room.y2 + 1):
            for x in range(room.x1 - 1, room.x2 + 1):
                self.tiles[x][y].occupied = True

        # Add special (named) rooms to a list so they can be called later
        if room.name:
            self.rooms[room.name] = room

        return entities

    def count_walls(self, n, x, y):
        wall_count = 0

        for r in range(-n, n + 1):
            for c in range(-n, n + 1):
                if x + r >= self.width or x + r <= 0 or y + c >= self.height or y + c <= 0:
                    wall_count += 1
                elif self.tiles[x + r][y + c].blocked:
                    wall_count += 1

        return wall_count

    def get_rand_unoccupied_space(self, w, h):
        x1 = randint(2, self.width - w - 2)
        y1 = randint(2, self.height - h - 2)
        x2 = x1 + w
        y2 = y1 + h
        while (self.tiles[x1][y1].occupied or
               self.tiles[x2][y2].occupied or
               self.tiles[x2][y1].occupied or
               self.tiles[x1][y2].occupied):
            x1 = randint(1, self.width - w - 1)
            y1 = randint(1, self.height - h - 1)
            x2 = x1 + w
            y2 = y1 + h

        return x1, y1

    def generate_hub(self):

        # Set ground tiles
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.tiles[x][y].color = "#423023"
                self.tiles[x][y].char = tilemap()["ground_soil"][randint(
                    0, (len(tilemap()["ground_soil"]) - 1))]

        # Generate a house
        w = h = 10
        # x1, y1 = self.get_rand_unoccupied_space(w, h)
        # home = Room(x1, y1, w, h, "#6b3d24", "#423023", wall="brick", floor="floor_wood", name="home")
        # objects = self.create_room(home)
        # door_home = self.create_door(home, "open", random=True)
        objects = []
        shaman_room = TiledRoom(name="home", lightness=0.8, filename="hub_shaman")
        x1, y1 = self.get_rand_unoccupied_space(w, h)
        shaman_room.update_coordinates(x1, y1)
        objects.extend(self.create_room(shaman_room))

        # Generate dungeon entrance
        # Make sure room doesn't overlap with existing rooms
        w = h = 10
        x1, y1 = self.get_rand_unoccupied_space(w, h)
        d_entrance = Room(x1, y1, w, h, "dark amber", "darkest amber", wall="brick", name="d_entrance")

        objects.extend(self.create_room(d_entrance))
        door_d_entrance = self.create_door(d_entrance, "locked", random=True)

        graveyard = TiledRoom(name="graveyard", lightness=0.5, filename="graveyard")
        x1, y1 = self.get_rand_unoccupied_space(w, h)
        graveyard.update_coordinates(x1, y1)
        objects.extend(self.create_room(graveyard))

        doors = [door_d_entrance]

        objects.extend(self.generate_trees(1, 1, self.width - 1, self.height - 1, 20))

        center_x, center_y = self.rooms["d_entrance"].get_center()

        stairs_component = Stairs(("hub", center_x, center_y), ["debug"], "stairs down", 0)
        stairs_down = Entity(center_x, center_y, 1, tilemap()["stairs"]["down"], "dark amber",
                             "stairs to a mysterious cavern", stairs=stairs_component)
        stairs_down.xtra_info = "You feel an ominous presence. Go down with '<' or '>'"
        self.tiles[center_x][center_y].entities_on_tile.append(stairs_down)
        self.create_decor()
        # objects = flatten(objects)
        map_stairs = [stairs_down]
        map_items = []
        map_objects = []
        for obj in objects:
            if obj.door:
                doors.append(obj)
            elif obj.stairs:
                map_stairs.append(obj)
            elif obj.item:
                map_items.append(obj)
            else:
                map_objects.append(obj)

        entities = {"objects": objects, "stairs": map_stairs, "doors": doors, "items": map_items}
        return entities

    def room_addition(self, entities=None, world_tendency=0):

        if entities is None:
            entities = {}
        self.roomAddition.generateLevel(self.width, self.height)
        forest_colors = get_forest_colors(world_tendency)
        dngn_color = get_dngn_colors(world_tendency)
        objects = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.tiles[x][y].color = dngn_color
                self.tiles[x][y].char = tilemap()["ground_soil"][randint(
                    0, (len(tilemap()["ground_soil"]) - 1))]
                if self.roomAddition.level[x][y] == 1:
                    self.tiles[x][y].spawnable = False

                    # Don't make unvisible trees entities to save in performance
                    if self.count_walls(1, x, y) < 8:

                        if abs(world_tendency) * 33 > randint(1, 100):
                            name = "dead tree"
                            char = tilemap()["dead_tree"][randint(0, (len(tilemap()["dead_tree"]) - 1))]
                            wall_component = Wall(name)
                            wall = Entity(x, y, 2, char, forest_colors[randint(0, len(forest_colors)-1)],
                                          name, wall=wall_component)
                            self.tiles[x][y].entities_on_tile.append(wall)
                            wall_component.set_attributes(self)
                            objects.append(wall)
                        else:
                            name = "tree"
                            char = tilemap()["tree"][randint(0, (len(tilemap()["tree"]) - 1))]
                            wall_component = Wall(name)
                            wall = Entity(x, y, 2, char, forest_colors[randint(0, len(forest_colors)-1)],
                                          name, wall=wall_component)
                            self.tiles[x][y].entities_on_tile.append(wall)
                            wall_component.set_attributes(self)
                            objects.append(wall)

                else:
                    self.tiles[x][y].spawnable = True

        entities["objects"] = objects

        return entities

    def random_walk(self, entities=None, world_tendency=0):

        if entities is None:
            entities = {}
        self.drunkardsWalk.generateLevel(self.width, self.height)
        forest_colors = get_forest_colors(world_tendency)
        objects = []

        for y in range(0, self.height):
            for x in range(0, self.width):
                self.tiles[x][y].color = "darkest gray"
                self.tiles[x][y].char = tilemap()["ground_soil"][randint(
                    0, (len(tilemap()["ground_soil"]) - 1))]
                if self.drunkardsWalk.level[x][y] == 1:

                    if abs(world_tendency) * 33 > randint(1, 100):
                        name = "dead tree"
                        char = tilemap()["dead_tree"][randint(0, (len(tilemap()["dead_tree"]) - 1))]
                        wall_component = Wall(name)
                        wall = Entity(x, y, 2, char, forest_colors[randint(0, 4)], name, wall=wall_component)
                        self.tiles[x][y].entities_on_tile.append(wall)
                        wall_component.set_attributes(self)
                        objects.append(wall)
                    else:
                        self.tiles[x][y].char = " "
                        name = "tree"
                        char = tilemap()["tree"][randint(0, (len(tilemap()["tree"]) - 1))]
                        wall_component = Wall(name)
                        wall = Entity(x, y, 2, char, forest_colors[randint(0, 4)], name, wall=wall_component)
                        self.tiles[x][y].entities_on_tile.append(wall)
                        wall_component.set_attributes(self)
                        objects.append(wall)

                    self.tiles[x][y].spawnable = False

                else:
                    self.tiles[x][y].spawnable = True

        objects = flatten(objects)
        entities["objects"] = objects
        return entities

    def generate_forest(self, world_tendency):

        entities = []
        cavern_colors = get_dngn_colors(world_tendency)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.tiles[x][y].color = cavern_colors[5]
                self.tiles[x][y].char = tilemap()["ground_soil"][randint(
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
            entities.append(self.generate_trees(dx, dy, width, height, freq, world_tendency))

        self.create_decor(world_tendency)

        return entities

    def generate_trees(self, dx, dy, width, height, freq, world_tendency=0):
        """Generate a forest to a rectangular area."""

        forest_colors = get_forest_colors(world_tendency)
        entities = []
        for y in range(dy, height):
            for x in range(dx, width):
                if not self.tiles[x][y].occupied:
                    self.tiles[x][y].spawnable = False

                    # Generate forest tiles
                    if randint(1, 100) < freq:

                        if abs(world_tendency) * 33 > randint(1, 100):
                            name = "dead tree"
                            char = tilemap()["dead_tree"][randint(0, (len(tilemap()["dead_tree"]) - 1))]
                            wall_component = Wall(name)
                            wall = Entity(x, y, 2, char, forest_colors[randint(0, 4)], name, wall=wall_component)
                            self.tiles[x][y].entities_on_tile.append(wall)
                            wall_component.set_attributes(self)
                            entities.append(wall)
                        else:
                            name = "tree"
                            char = tilemap()["tree"][randint(0, (len(tilemap()["tree"]) - 1))]
                            wall_component = Wall(name)
                            wall = Entity(x, y, 2, char, forest_colors[randint(0, 4)], name, wall=wall_component)
                            self.tiles[x][y].entities_on_tile.append(wall)
                            wall_component.set_attributes(self)
                            entities.append(wall)

        return entities

    def generate_cavern(self, entities):

        cavern_colors = ["lightest amber",
                         "lighter amber",
                         "light amber",
                         "dark amber",
                         "darker amber",
                         "darkest amber"]

        for y in range(self.height):
            for x in range(self.width):

                self.tiles[x][y].color = cavern_colors[4]
                self.tiles[x][y].char = tilemap()["ground_moss"][randint(
                    0, (len(tilemap()["ground_moss"]) - 1))]
                self.tiles[x][y].visited = False
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                freq = randint(1, 100)
                if freq < 50:
                    self.tiles[x][y].color = cavern_colors[4]
                    self.tiles[x][y].char = tilemap()["moss"][randint(
                        0, (len(tilemap()["moss"]) - 1))]
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True

        for i in range(5):
            for x in range(self.width):
                for y in range(self.height):
                    wall_one_away = self.count_walls(1, x, y)
                    wall_two_away = self.count_walls(2, x, y)

                    if wall_one_away >= 5 or wall_two_away <= 2:
                        self.tiles[x][y].color = cavern_colors[4]
                        self.tiles[x][y].char = tilemap()["moss"][randint(
                            0, (len(tilemap()["moss"]) - 1))]
                        self.tiles[x][y].blocked = True
                        self.tiles[x][y].block_sight = True

                    else:
                        self.tiles[x][y].blocked = False
                        self.tiles[x][y].block_sight = False
                        self.tiles[x][y].char = " "

        # Smooth out singular walls in empty spaces

        # =======================================================================
        # for i in range (5):
        #     for x in range (self.width):
        #         for y in range (self.height):
        #             wall_one_away = self.count_walls(1, x, y)
        #
        #             if wall_one_away >= 5:
        #                 self.tiles[x][y].color[1] = cavern_colors[4]
        #                 self.tiles[x][y].char = tilemap()["moss"][randint(
        #                     0, (len(tilemap()["moss"]) - 1))]
        #                 self.tiles[x][y].blocked = True
        #                 self.tiles[x][y].block_sight = False
        #             else:
        #                 self.tiles[x][y].blocked = False
        #                 self.tiles[x][y].block_sight = False
        #                 self.tiles[x][y].char = " "
        # =======================================================================

        for y in range(self.height):
            for x in range(self.width):
                wall_one_away = self.count_walls(1, x, y)

                if (x == 1 or x == self.width - 2 or
                        y == 1 or y == self.height - 2):
                    self.tiles[x][y].color = cavern_colors[4]
                    self.tiles[x][y].char = tilemap()["moss"][randint(
                        0, (len(tilemap()["moss"]) - 1))]
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
        caverns = caverns[:len(caverns) - 1]
        objects = []
        for i in range(0, len(caverns)):
            for j in range(0, len(caverns[i])):
                color = cavern_colors[4]
                name = "moss"
                char = tilemap()["moss"][randint(
                    0, (len(tilemap()["moss"]) - 1))]
                wall_component = Wall(name)
                wall = Entity(i, j, 2, char, color, name, wall=wall_component)
                wall_component.set_attributes(self)
                objects.append(wall)

        # Get random position in the main cave
        pos = randint(0, len(main_cave) - 1)
        px, py = main_cave[pos].x, main_cave[pos].y

        stairs_current_floor = []
        # On the first floor there is only one set of stairs up which leads back to hub
        if self.dungeon_level == 1:
            stairs_component = Stairs(("cavern1", px, py), ["hub", entities["stairs"][1].stairs.source[1],
                                                            entities["stairs"][1].stairs.source[2]], "hub",
                                      self.dungeon_level)
            entities["stairs"][1].stairs.destination.extend((px, py))
            stairs_up = Entity(px, py, 1, tilemap()["stairs"]["up"], "dark amber", "stairs up", stairs=stairs_component)
            stairs_current_floor.append(stairs_up)
        # Make as many stairs upstairs as previous floor had stairs down
        else:
            for i, entity in enumerate(entities["stairs"]):
                if entity.stairs.name == "stairs down":
                    pos = randint(0, len(main_cave) - 1)
                    px, py = main_cave[pos].x, main_cave[pos].y
                    stairs_component = Stairs(("cavern" + str(self.dungeon_level), px, py),
                                              ["cavern" + str(self.dungeon_level - 1), entity.stairs.source[1],
                                               entity.stairs.source[2]], "stairs up", self.dungeon_level)
                    stairs_up = Entity(px, py, 1, tilemap()["stairs"]["up"], "dark amber", "stairs up",
                                       stairs=stairs_component)
                    self.tiles[px][py].entities_on_tile.append(stairs_up)
                    # Connect the stairs with previous level's down going stairs
                    entity.stairs.destination.extend((px, py))
                    stairs_current_floor.append(stairs_up)

        entities = {}

        # Create 3 sets of stairs down
        for i in range(1, 4):
            pos = randint(0, len(main_cave) - 1)
            px, py = main_cave[pos].x, main_cave[pos].y
            stairs_component = Stairs(("cavern" + str(self.dungeon_level), px, py),
                                      ["cavern" + str(self.dungeon_level + 1)], "stairs down", self.dungeon_level)
            stairs_down = Entity(px, py, 1, tilemap()["stairs"]["down"], "dark amber", "stairs down",
                                 stairs=stairs_component)
            self.tiles[px][py].entities_on_tile.append(stairs_down)
            stairs_current_floor.append(stairs_down)

        entities["stairs"] = []
        for entity in stairs_current_floor:
            entities["stairs"].append(entity)

        entities["objects"] = objects

        return entities

    def is_blocked(self, x, y):

        if x >= self.width - 1 or x <= 0 or y >= self.height - 1 or y <= 0:
            return True
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, player, entities, world_tendency=None, stairs=None):

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

        # Remove wall entities under doors
        door_coords = []
        if "doors" in entities:
            for door in entities["doors"]:
                door_coords.append((door.x, door.y))
            for door in door_coords:
                for i, entity in enumerate(entities["objects"]):
                    if entity.x == door[0] and entity.y == door[1] and entity.wall:
                        self.tiles[entity.x][entity.y].entities_on_tile.remove(entity)
                        del entities["objects"][i]

        if stairs:
            player.x, player.y = stairs.destination[1], stairs.destination[2]

        # Player spawning point has been set in all scenarios, now place rest of the entities
        entities["player"] = [player]
        entities["monsters"] = []

        if self.name == "debug":
            player.x, player.y = 2, 2
            player.fighter.max_hp = 99999999
            player.fighter.hp = 99999999
            number_of_monsters = 1
            monsters = []
            # for x, y in tilemap()["monsters"].items():
            #     if x == "crow":
            #         monsters.append((x, y))

            for x, y in tilemap()["unique_monsters"].items():
                if x == "keeper of dreams":
                    monsters.append((x, y))

            for i in range(number_of_monsters):
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y):
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)

                if not any([entity for entity in entities["monsters"] if entity.x == x and entity.y == y]):
                    # r = randint(0, 2)
                    name, char = monsters[0]
                    color = get_monster_color(name)
                    fighter_component = get_fighter_stats(name)
                    ai_component = get_fighter_ai(name)
                    light_component = LightSource(radius=fighter_component.fov)
                    monster = Entity(x, y, 3, char,
                                     color, name, blocks=True, fighter=fighter_component, ai=ai_component,
                                     light_source=light_component, boss=True)
                    monster.xtra_info = "It appears to be a terrifying red dragon."
                    monster.light_source.initialize_fov(self)
                    self.tiles[x][y].entities_on_tile.append(monster)
                    self.tiles[x][y+1].entities_on_tile.append(monster)
                    self.tiles[x+1][y + 1].entities_on_tile.append(monster)
                    self.tiles[x+1][y].entities_on_tile.append(monster)
                    monster.occupied_tiles = [(x, y), (x, y+1), (x+1, y+1), (x+1, y)]
                    entities["monsters"].append(monster)

        if stairs and self.name == "cavern" + str(stairs.floor + 1):

            number_of_monsters = randint(self.width / 2 - 40, self.width / 2 - 20)
            # number_of_monsters = 0
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
                    # r = randint(0, 2)
                    name, char = monsters[0]
                    color = get_monster_color(name)
                    fighter_component = get_fighter_stats(name)
                    ai_component = get_fighter_ai(name)
                    light_component = LightSource(radius=fighter_component.fov)
                    monster = Entity(x, y, 3, char,
                                     color, name, blocks=True, fighter=fighter_component, ai=ai_component,
                                     light_source=light_component)
                    monster.light_source.initialize_fov(self)
                    self.tiles[x][y].entities_on_tile.append(monster)
                    entities["monsters"].append(monster)

        self.tiles[player.x][player.y].entities_on_tile.append(player)

        if self.name == "dream":

            self.create_decor(world_tendency)
            number_of_monsters = randint(self.width / 2 - 30, self.width / 2)
            monsters = []

            if world_tendency < 0:
                for x, y in tilemap()["monsters_chaos"].items():
                    monsters.append((x, y))
            elif world_tendency > 0:
                for x, y in tilemap()["monsters_light"].items():
                    monsters.append((x, y))
            else:
                for x, y in tilemap()["monsters"].items():
                    monsters.append((x, y))
            monsters.sort()
            spawn_rates = get_spawn_rates(monsters)

            monster_pool = choices(monsters, spawn_rates, k=number_of_monsters)

            for mon in monster_pool:
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y) or x == player.x and y == player.y:
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)

                if not any([entity for entity in entities["monsters"] if entity.x == x and entity.y == y]):
                    name = mon[0]
                    char = mon[1]
                    color = get_monster_color(name)
                    fighter_component = get_fighter_stats(name)
                    ai_component = get_fighter_ai(name)
                    light_component = LightSource(radius=fighter_component.fov)
                    monster = Entity(x, y, 3, char,
                                     color, name, blocks=True, fighter=fighter_component, ai=ai_component,
                                     light_source=light_component)
                    monster.light_source.initialize_fov(self)
                    self.tiles[x][y].entities_on_tile.append(monster)
                    entities["monsters"].append(monster)

        return player, entities

    def create_door(self, room=None, status="open", tile=None, name="door", color=None, random=False, x=None, y=None):

        """
        Create a door entity in map. If no coordinates are given,
        pick a random (x, y) from room walls.
        If any of the room walls are against the map border,
        make sure that door cannot be placed there.
        """

        walls = room.get_walls()
        if random:
            door_seed = randint(0, len(room.get_walls()) - 1)

            while walls[door_seed][0] == 1 or walls[door_seed][0] == room.w - 1 or walls[door_seed][1] == 1 or \
                    walls[door_seed][1] == room.h - 1:
                door_seed = randint(0, len(room.get_walls()) - 1)
            x = walls[door_seed][0]
            y = walls[door_seed][1]

        if tile is None:
            tile = tilemap()["door"][status]
        if color is None:
            color = "dark amber"
        door_component = Door(room.name, status)
        door = Entity(x, y, 2, tile, color, name,
                      door=door_component, stand_on_messages=False)
        self.tiles[x][y].entities_on_tile.append(door)

        if status == "open":
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
        else:
            self.tiles[x][y].blocked = True
            self.tiles[x][y].block_sight = True

        return door

    def scan_doors(self, room):
        doors_open = [0xE500 + 21, 0xE500 + 23, 0xE500 + 25, 0xE500 + 29, 0xE500 + 31, 0xE500 + 33, 0xE500 + 35,
                      0xE500 + 37, 0xE500 + 103]
        doors_closed = [0xE500 + 20, 0xE500 + 22, 0xE500 + 24, 0xE500 + 26, 0xE500 + 27, 0xE500 + 28, 0xE500 + 30,
                        0xE500 + 32, 0xE500 + 36, 0xE500 + 102]
        doors = []
        for y, row in enumerate(room.layers["terrain_objects"]):
            for x, char in enumerate(row):
                if char in doors_open:
                    name, color = name_color_from_value(char)
                    doors.append(self.create_door(room, "open", char, name=name, color=color,
                                                  x=room.x1 + x, y=room.y1 + y))
                if char in doors_closed:
                    name, color = name_color_from_value(char)
                    doors.append(self.create_door(room, "closed", char, name=name, color=color,
                                                  x=room.x1 + x, y=room.y1 + y))

        return doors

    def create_decor(self, world_tendency=1):

        if variables.gfx == "ascii":
            return
        # Generate rocks & rubble on floor tiles
        decor_odds = 0.1
        decor_options = ["rocks", "bones", "flowers", "plants", "mushrooms"]
        decormap = np.random.rand(self.height, self.width)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.is_blocked(x, y) and not self.tiles[x][y].occupied:

                    if decormap[y, x] < decor_odds and len(self.tiles[x][y].layers) == 0:
                        option = randint(0, len(decor_options)-1)

                        if option == 0:
                            name, color = name_color_from_value(tilemap("oryx")["rocks"][0]-0xE500)
                            char = tilemap()["rocks"][randint(
                                0, (len(tilemap()["rocks"]) - 1))]
                            self.tiles[x][y].layers.append((char, color))
                            self.tiles[x][y].name = name

                        if option == 1:
                            name, color = name_color_from_value(tilemap("oryx")["plants"][0]-0xE500)
                            char = tilemap()["plants"][randint(
                                0, (len(tilemap()["plants"]) - 1))]
                            self.tiles[x][y].layers.append((char, color))
                            self.tiles[x][y].name = name

                        if option == 2:
                            name, color = name_color_from_value(tilemap("oryx")["flowers"][0]-0xE500)
                            char = tilemap()["flowers"][randint(
                                0, (len(tilemap()["flowers"]) - 1))]
                            self.tiles[x][y].layers.append((char, color))
                            self.tiles[x][y].name = name

                        if option == 3:
                            name, color = name_color_from_value(tilemap("oryx")["mushrooms"]-0xE500)
                            char = tilemap()["mushrooms"]
                            self.tiles[x][y].layers.append((char, color))
                            self.tiles[x][y].name = name

                    if world_tendency < 0:
                        if randint(1, 4) >= self.tiles[x][y].seed and len(self.tiles[x][y].layers) == 0:
                            if abs(world_tendency) * 33 > randint(1, 100):
                                name, color = name_color_from_value(tilemap("oryx")["bones"][0]-0xE500)
                                char = tilemap()["bones"][randint(
                                    0, (len(tilemap()["bones"]) - 1))]
                                self.tiles[x][y].layers.append((char, color))
                                self.tiles[x][y].name = name

    @staticmethod
    def entity_at_coordinates(entities, x, y):
        result = []
        for category in entities:
            for entity in entities[category]:
                if entity.x == x and entity.y == y:
                    result.append(entity)
        return result


class Room:
    def __init__(self, x1=0, y1=0, w=5, h=5, wall_color="dark gray", floor_color="darkest amber",
                 wall="brick", floor="floor", tiled=False, name=None, lightness=1.0):
        self.x1 = x1
        self.y1 = y1
        self.w = w
        self.h = h
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h
        self.floor = floor
        self.wall = wall
        self.wall_color = wall_color
        self.floor_color = floor_color
        self.tiled = tiled
        self.name = name
        self.lightness = lightness

    def update_coordinates(self, x1, y1):
        self.x1 = x1
        self.y1 = y1
        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h

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


class TiledRoom(Room):
    def __init__(self, x1=0, y1=0, w=0, h=0, wall_color="dark gray", floor_color="darkest amber",
                 floor="floor", tiled=True, name=None, lightness=1.0, filename=None):
        Room.__init__(self, x1=x1, y1=y1, w=w, h=h, wall_color=wall_color, floor_color=floor_color,
                      floor=floor, tiled=tiled, name=name, lightness=lightness)
        self.layers = None
        self.tiled_reader(filename)

    def tiled_reader(self, name):
        tree = ET.parse("./tilesets/" + name + ".tmx")
        root = tree.getroot()
        layers = [ None, None, None ]
        for layer in root.iter("layer"):

            data = layer.find("data").text[1:-1].splitlines()
            self.h = len(data)
            self.w = len(data[0].split(",")) - 1
            tiled_map = []
            for row in data:
                if row[-1] == ",":
                    new_row = row.split(",")[:-1]
                else:
                    new_row = row.split(",")
                for i, char in enumerate(new_row):
                    value = int(char) - 1 if int(char) > 0 else 0
                    new_row[i] = value

                tiled_map.append(new_row)

            layers[int(layer.attrib["name"])] = tiled_map

        self.layers = layers
