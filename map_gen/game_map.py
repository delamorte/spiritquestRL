from random import choice, choices, randint

import numpy as np
from tcod.map import compute_fov

from components.AI.ai_basic import AIBasic
from components.AI.ai_caster import AICaster
from components.abilities import Abilities
from components.animations import Animations
from components.dialogue import Dialogue
from components.entity import Entity
from components.fighter import Fighter
from components.item import Item
from components.light_source import LightSource
from components.npc import Npc
from components.openable import Openable
from components.stairs import Stairs
from components.status_effects import StatusEffects
from components.wall import Wall
from map_gen.algorithms.cellular import CellularAutomata
from map_gen.algorithms.drunkards import DrunkardsWalk
from map_gen.algorithms.messy_bsp import MessyBSPTree
from map_gen.algorithms.room_addition import RoomAddition
from map_gen.dungeon import TiledRoom, Room
from map_gen.tile import Tile
from map_gen.tilemap import get_tile, get_color, get_tile_by_value, get_tile_object, get_tile_variant, \
    get_fighters_by_attribute


class GameMap:
    def __init__(self, width, height, name, biome=None, title=None, dungeon_level=0):
        self.algorithm = None
        self.owner = None
        self.entities = None
        self.width = width
        self.height = height
        self.name = name
        self.biome = biome
        self.title = title if title is not None else name
        self.dungeon_level = dungeon_level
        self.rooms = {}
        self.transparent = None
        self.visible = None
        self.explored = None
        self.light_map = None
        self.tiles = self.initialize_tiles()

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
                    tiles[x][y].char = " "

        self.visible = np.full((self.width, self.height), fill_value=False)
        self.explored = np.full((self.width, self.height), fill_value=False)
        self.light_map = np.ones_like(self.visible, dtype=float)

        return tiles

    def recompute_fov(self, entity):

        x, y = entity.x, entity.y
        radius = entity.light_source.radius

        # Update transparency map
        transparency = np.frompyfunc(lambda tile: not tile.block_sight, 1, 1)
        self.transparent = transparency(self.tiles)

        # Update visible tiles
        self.visible[:] = compute_fov(
            self.transparent,
            (x, y),
            radius=radius
        )
        self.light_map = np.ones_like(self.visible, dtype=float)
        # If a tile is "visible" it should be added to "explored".
        self.explored |= self.visible

    def get_neighbours(self, entity, radius=1, include_self=False, fighters=False, mark_area=False,
                       algorithm="square", empty_tiles=False, exclude_player=False):
        """
        :param exclude_player: excludes the player from the entities
        :param empty_tiles: return empty tiles around entity
        :param algorithm: the shape of the targeting area
        :param mark_area: flags the neighbour area so draw_map can highlight it
        :param entity:
        :param radius: radius
        :param include_self: include self (center) in the list of entities
        :param fighters: return only fighting entities
        :return: list of entities surrounding the center in radius n
        """

        if algorithm == "melee":
            algorithm = "square"
            radius = 1

        entities = []

        def n_closest(x, n, d=1):
            return x[n[0] - d:n[0] + d + 1, n[1] - d:n[1] + d + 1]

        def n_disc(array):
            a, b = entity.x, entity.y
            n = self.tiles.shape[0]
            r = radius

            y, x = np.ogrid[-a:n - a, -b:n - b]
            mask = x * x + y * y <= r * r

            return array[mask]

        if algorithm == "disc":
            neighbours = n_disc(self.tiles).flatten()
        elif algorithm == "square":
            neighbours = n_closest(self.tiles, (entity.x, entity.y), d=radius).flatten()
        else:
            neighbours = n_closest(self.tiles, (entity.x, entity.y), d=radius).flatten()

        tiles = []

        for tile in neighbours:
            if empty_tiles:
                if not tile.blocked and not tile.blocking_entity:
                    tiles.append(tile)
            else:
                if mark_area:
                    tile.targeting_zone = True
                else:
                    tile.targeting_zone = False
                if tile.entities_on_tile:
                    if not include_self and tile.blocking_entity == entity:
                        continue
                    elif fighters and exclude_player:
                        fighting_entities = [entity for entity in tile.entities_on_tile if
                                             entity.fighter and not entity.player]
                        entities.extend(fighting_entities)
                    elif fighters:
                        fighting_entities = [entity for entity in tile.entities_on_tile if entity.fighter]
                        entities.extend(fighting_entities)
                    else:
                        entities.extend(tile.entities_on_tile)
        if empty_tiles:
            return list(filter(lambda tile: self.visible[tile.x, tile.y], tiles))
        else:
            return list(filter(lambda entity: self.visible[entity.x, entity.y], entities))

    def process_room(self, room, exclude_light_y=None):
        entities = []
        for y in range(room.y1, room.y2):
            for x in range(room.x1, room.x2):
                self.tiles[x][y].occupied = True
                if exclude_light_y is not None and y not in exclude_light_y:
                    self.tiles[x][y].natural_light_level = room.lightness

                if room.tiled:
                    ground = room.layers[0][y - room.y1][x - room.x1]
                    ground_top = room.layers[1][y - room.y1][x - room.x1]
                    entity = room.layers[2][y - room.y1][x - room.x1]

                    if ground != 0:
                        name = get_tile_by_value(ground)
                        ground_char = get_tile(name)
                        color = get_color(name, mod=self.owner.world_tendency)
                        self.tiles[x][y].char = ground_char
                        if color is not None:
                            self.tiles[x][y].color = color

                    if ground_top != 0:
                        name = get_tile_by_value(ground_top)
                        ground_top_char = get_tile(name)
                        color = get_color(name, mod=self.owner.world_tendency)
                        self.tiles[x][y].layers.append((ground_top_char, color))

                    if entity != 0:
                        name = get_tile_by_value(entity)
                        char = get_tile_variant(name, variant_char=entity)
                        tile = get_tile_object(name)
                        color = get_color(name, mod=self.owner.world_tendency)

                        if tile["openable"]:
                            name = tile["name"]
                            door_component = Openable(name, char)
                            door = Entity(x, y, 1,
                                          color, name, tile=tile, door=door_component, stand_on_messages=False)
                            self.tiles[x][y].add_entity(door)
                            self.tiles[x][y].is_door = True
                            self.tiles[x][y].door = door_component
                            door_component.set_state(door_component.state, self)
                            entities.append(door)
                        elif tile["interactable"] or tile["pickable"]:
                            item_component = Item(name, pickable=tile["pickable"], interactable=tile["interactable"],
                                                  light_source=tile["light_source"])
                            item = Entity(x, y, 1,
                                          color, name, tile=tile, item=item_component)
                            if item.name == "flask":  # For testing "reveal" skill
                                item.hidden = True
                            self.tiles[x][y].add_entity(item)
                            item_component.set_attributes(self)
                            entities.append(item)
                        elif tile["stairs"]:
                            stairs_component = Stairs(("hub", x, y), ["dream"], name)
                            portal = Entity(x, y, 1, color, name, tile=tile,
                                            stairs=stairs_component)
                            self.tiles[x][y].add_entity(portal)
                            stairs_component.set_attributes(self)
                            portal.xtra_info = "Meditate and go to dream world with '<' or '>'"
                            entities.append(portal)
                        else:
                            wall_component = Wall(name=name, tile=tile)
                            wall = Entity(x, y, 1,
                                          color, name, char=char, tile=tile, wall=wall_component)
                            self.tiles[x][y].add_entity(wall)
                            wall_component.set_attributes(self)
                            entities.append(wall)

                else:
                    # Horizontal walls
                    if (y == room.y1 or y == room.y2 - 1) and 0 <= x <= room.x2 - 1:
                        wall = self.create_wall(room.wall, x, y, 0)
                        entities.append(wall)
                    # Vertical walls
                    elif (x == room.x1 or x == room.x2 - 1) and 0 <= y < room.y2 - 1:
                        wall = self.create_wall(room.wall, x, y, 2)
                        entities.append(wall)
                    # Upper right corner
                    elif x == room.x2 and y == room.y1:
                        wall = self.create_wall(room.wall, x, y, 1)
                        entities.append(wall)
                    # Lower right corner
                    elif x == room.x2 and y == room.y2:
                        wall = self.create_wall(room.wall, x, y, 3)
                        entities.append(wall)
                    # Lower left corner
                    elif x == room.x1 and y == room.y2:
                        wall = self.create_wall(room.wall, x, y, 5)
                        entities.append(wall)
                    # Upper left corner
                    elif x == room.x1 and y == room.y1:
                        wall = self.create_wall(room.wall, x, y, 7)
                        entities.append(wall)

                    else:
                        self.tiles[x][y].color = get_color(room.floor)
                        self.tiles[x][y].char = get_tile(room.floor)
                        self.tiles[x][y].spawnable = True

        # Make sure nothing can block room wall immediate neighbours
        for y in range(room.y1 - 1, room.y2 + 1):
            for x in range(room.x1 - 1, room.x2 + 1):
                self.tiles[x][y].occupied = True

        # Add special (named) rooms to a list so they can be called later
        if room.name:
            self.rooms[room.name] = room

        return entities

    def create_wall(self, name, x, y, index):
        """
        :param name:
        :param x:
        :param y:
        :param index: 0 = horizontal, 2 = vertical, 1 = NE, 3 = SE, 5 = SW, 7 = NW
        :return: wall entity
        """
        tile = get_tile_object(name)
        color = get_color(name)
        wall_component = Wall(name=name, tile=tile)
        tile_char = get_tile_variant(name, index)
        wall = Entity(x, y, 1,
                      color, name, tile=tile, char=tile_char, wall=wall_component)
        self.tiles[x][y].add_entity(wall)
        wall_component.set_attributes(self)
        return wall

    def count_walls(self, n, x, y):
        wall_count = 0

        for r in range(-n, n + 1):
            for c in range(-n, n + 1):
                if x + r >= self.width or x + r <= 0 or y + c >= self.height or y + c <= 0:
                    wall_count += 1
                elif self.tiles[x + r][y + c].blocked:
                    wall_count += 1

        return wall_count

    def get_random_unoccupied_space(self, w, h):
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

    # TODO: Think of a better way to do this
    def get_random_unoccupied_space_near_room(self, room, radius=2):
        x = randint(room.x1 - radius, room.x2 + radius)
        y = randint(room.y1 - radius, room.y2 + radius)

        while self.tiles[x][y].occupied or self.tiles[x][y].entities_on_tile or len(self.tiles[x][y].layers) > 0:
            x = randint(room.x1 - radius, room.x2 + radius)
            y = randint(room.y1 - radius, room.y2 + radius)

        if radius == 2:
            x2 = x + 1
            y2 = y + 1
            self.tiles[x2][y].entities_on_tile = []
            self.tiles[x2][y].layers = []
            self.tiles[x2][y2].entities_on_tile = []
            self.tiles[x2][y2].layers = []
            self.tiles[x][y2].entities_on_tile = []
            self.tiles[x][y2].layers = []

        return x, y

    def generate_hub(self):

        # Set ground tiles
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.tiles[x][y].color = "#423023"
                self.tiles[x][y].char = get_tile("ground_soil")

        # Generate a house
        w = h = 10
        # x1, y1 = self.get_rand_unoccupied_space(w, h)
        # home = Room(x1, y1, w, h, "#6b3d24", "#423023", wall="wall_brick", floor="floor_wood", name="home")
        # objects = self.process_room(home)
        # door_home = self.create_door(home, "open", random=True)
        objects = []
        shaman_room = TiledRoom(name="home", lightness=0.8, filename="hub_shaman")
        x1, y1 = self.get_random_unoccupied_space(w, h)
        shaman_room.update_coordinates(x1, y1)
        excludes_y = (shaman_room.y2-1,)
        objects.extend(self.process_room(shaman_room, exclude_light_y=excludes_y))

        # Generate dungeon entrance
        # Make sure room doesn't overlap with existing rooms
        w = h = 10
        x1, y1 = self.get_random_unoccupied_space(w, h)
        d_entrance = Room(x1, y1, w, h, "dark amber", "darkest amber", wall="wall_brick", name="d_entrance")

        objects.extend(self.process_room(d_entrance))
        door_d_entrance = self.create_door(d_entrance, "locked", random=True)

        graveyard = TiledRoom(name="graveyard", lightness=0.5, filename="graveyard")
        x1, y1 = self.get_random_unoccupied_space(w, h)
        graveyard.update_coordinates(x1, y1)
        excludes_y = (graveyard.y2-1, graveyard.y1,)
        objects.extend(self.process_room(graveyard, exclude_light_y=excludes_y))

        doors = [door_d_entrance]

        objects.extend(self.generate_trees(1, 1, self.width - 1, self.height - 1, 20))

        # objects.extend(self.create_entities())

        center_x, center_y = self.rooms["d_entrance"].get_center()

        stairs_component = Stairs(("hub", center_x, center_y), ["debug"], "stairs down", 0)
        char = get_tile("stairs_down")
        stairs_down = Entity(center_x, center_y, 1, "dark amber", "stairs to a mysterious cavern",
                             char=char, stairs=stairs_component)
        stairs_down.xtra_info = "You feel an ominous presence. Go down with '<' or '>'"
        self.tiles[center_x][center_y].add_entity(stairs_down)
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

        # Place player
        center_x, center_y = self.rooms["home"].get_center()
        self.owner.player.x, self.owner.player.y = center_x - 1, center_y - 1

        self.entities = {"objects": objects, "stairs": map_stairs, "doors": doors, "items": map_items, "npcs": []}

        npcs = []
        npc_name = "black crow king"
        npcs.append((npc_name, get_tile(npc_name)))
        location = self.get_random_unoccupied_space_near_room(shaman_room)
        self.create_entities(npcs, "npcs", location=location)

        transparency = np.frompyfunc(lambda tile: not tile.block_sight, 1, 1)
        self.transparent = transparency(self.tiles)

    def generate_biome(self):
        pass

    def generate_map(self, entities=None, name=None):

        if entities is None:
            entities = {}

        generators = {
                      "random_walk": DrunkardsWalk(self.width, self.height),
                      "messy_bsp": MessyBSPTree(self.width, self.height),
                      "cellular": CellularAutomata(self.width, self.height),
                      "room_addition": RoomAddition(self.width, self.height)
                     }

        if not name:
            map_algorithm = choice(list(generators.values()))

        else:
            map_algorithm = generators[name]

        self.algorithm = map_algorithm

        map_algorithm.generate_level()
        color = get_color("ground_soil")
        tree_color = get_color("tree", mod=self.owner.world_tendency)
        objects = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.tiles[x][y].color = color
                self.tiles[x][y].char = get_tile("ground_soil")
                if map_algorithm.level[x][y] == 1:
                    self.tiles[x][y].spawnable = False

                    # Don't make not visible trees entities to save in performance
                    if self.count_walls(1, x, y) < 8:

                        if self.owner.world_tendency < 0 and abs(self.owner.world_tendency) * 5 > randint(1, 100):
                            name = "tree_dead"
                            char = get_tile_variant(name)
                            dead_tree_color = get_color(name)
                            wall_component = Wall(name)
                            wall = Entity(x, y, 1, dead_tree_color, "dead tree",
                                          char=char, wall=wall_component)

                        else:
                            name = "tree"
                            char = get_tile_variant(name)
                            if (y == 0 and x == 0) or y % 5 == 0:
                                tree_color = get_color(name)
                            wall_component = Wall(name)
                            wall = Entity(x, y, 1, tree_color, name,
                                          char=char, wall=wall_component)
                        self.tiles[x][y].add_entity(wall)
                        wall_component.set_attributes(self)
                        objects.append(wall)

                else:
                    self.tiles[x][y].spawnable = True

        entities["objects"] = objects

        self.entities = entities
        transparency = np.frompyfunc(lambda tile: not tile.block_sight, 1, 1)
        self.transparent = transparency(self.tiles)

    def generate_forest(self):

        entities = []
        color = get_color("ground_soil")
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.tiles[x][y].color = color
                self.tiles[x][y].char = get_tile("ground_soil")
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
            entities.append(self.generate_trees(dx, dy, width, height, freq))

        self.create_decor()

        return entities

    def generate_trees(self, dx, dy, width, height, freq):
        """Generate a forest to a rectangular area."""

        entities = []
        tree_color = get_color("tree", mod=self.owner.world_tendency)
        for y in range(dy, height):
            for x in range(dx, width):
                if not self.tiles[x][y].occupied:
                    self.tiles[x][y].spawnable = False

                    # Generate forest tiles
                    if randint(1, 100) < freq:

                        if self.owner.world_tendency < 0 and abs(self.owner.world_tendency) * 5 > randint(1, 100):
                            name = "tree_dead"
                            char = get_tile_variant(name)
                            dead_tree_color = get_color(name)
                            wall_component = Wall(name)
                            wall = Entity(x, y, 1, dead_tree_color, "dead tree",
                                          char=char, wall=wall_component)

                        else:
                            name = "tree"
                            char = get_tile_variant(name)
                            if (y == 0 and x == 0) or y % 5 == 0:
                                tree_color = get_color(name)
                            wall_component = Wall(name)
                            wall = Entity(x, y, 1, tree_color, name,
                                          char=char, wall=wall_component)
                        self.tiles[x][y].add_entity(wall)
                        wall_component.set_attributes(self)
                        entities.append(wall)

        return entities

    def generate_cavern(self, entities):

        for y in range(self.height):
            for x in range(self.width):

                self.tiles[x][y].color = get_color("ground_moss")
                self.tiles[x][y].char = get_tile("ground_moss")
                self.tiles[x][y].visited = False
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                freq = randint(1, 100)
                if freq < 50:
                    self.tiles[x][y].color = get_color("moss")
                    self.tiles[x][y].char = get_tile("moss")
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True

        for i in range(5):
            for x in range(self.width):
                for y in range(self.height):
                    wall_one_away = self.count_walls(1, x, y)
                    wall_two_away = self.count_walls(2, x, y)

                    if wall_one_away >= 5 or wall_two_away <= 2:
                        self.tiles[x][y].color = get_color("moss")
                        self.tiles[x][y].char = get_tile("moss")
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
        #                 self.tiles[x][y].char = tilemap.data.tiles["moss"][randint(
        #                     0, (len(tilemap.data.tiles["moss"]) - 1))]
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
                    self.tiles[x][y].color = get_color("moss")
                    self.tiles[x][y].char = get_tile("moss")
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
                color = get_color("moss")
                name = "moss"
                char = get_tile("moss")
                wall_component = Wall(name)
                wall = Entity(i, j, 1, color, name, char=char, wall=wall_component)
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
            char = get_tile("stairs_up")
            stairs_up = Entity(px, py, 1, "dark amber", "stairs up", char=char, stairs=stairs_component)
            stairs_current_floor.append(stairs_up)
        # Make as many stairs upstairs as previous floor had stairs down
        else:
            for i, entity in enumerate(entities["stairs"]):
                if entity.stairs.name == "stairs down":
                    pos = randint(0, len(main_cave) - 1)
                    px, py = main_cave[pos].x, main_cave[pos].y
                    char = get_tile("stairs_up")
                    stairs_component = Stairs(("cavern" + str(self.dungeon_level), px, py),
                                              ["cavern" + str(self.dungeon_level - 1), entity.stairs.source[1],
                                               entity.stairs.source[2]], "stairs up", self.dungeon_level)
                    stairs_up = Entity(px, py, 1, "dark amber", "stairs up", char=char,
                                       stairs=stairs_component)
                    self.tiles[px][py].add_entity(stairs_up)
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
            char = get_tile("stairs_down")
            stairs_down = Entity(px, py, 1, "dark amber", "stairs down", char=char,
                                 stairs=stairs_component)
            self.tiles[px][py].add_entity(stairs_down)
            stairs_current_floor.append(stairs_down)

        entities["stairs"] = []
        for entity in stairs_current_floor:
            entities["stairs"].append(entity)

        entities["objects"] = objects

        self.entities = entities

    def is_blocked(self, x, y):

        if x >= self.width - 1 or x <= 0 or y >= self.height - 1 or y <= 0:
            return True
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self):

        # Place player
        player = self.owner.player
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
        if "doors" in self.entities:
            for door in self.entities["doors"]:
                door_coords.append((door.x, door.y))
            for door in door_coords:
                for i, entity in enumerate(self.entities["objects"]):
                    if entity.x == door[0] and entity.y == door[1] and entity.wall:
                        self.tiles[entity.x][entity.y].remove_entity(entity)
                        del self.entities["objects"][i]

        stairs = None
        if "stairs" in self.entities:
            for entity in self.entities["stairs"]:
                if player.x == entity.x and player.y == entity.y:
                    stairs = entity.stairs
                    player.x, player.y = stairs.destination[1], stairs.destination[2]

        # Player spawning point has been set in all scenarios, now place rest of the entities
        self.entities["monsters"] = []
        self.entities["allies"] = []
        self.entities["npcs"] = []
        self.entities["player"] = [player]

        if self.name == "debug":
            player.x, player.y = 2, 2
            player.fighter.max_hp = 99999999
            player.fighter.hp = 99999999
            number_of_monsters = 1
            monsters = []
            # for x, y in tilemap.data.tiles["monsters"].items():
            #     if x == "crow":
            #         monsters.append((x, y))
            boss = "keeper of dreams"
            tile = get_tile("keeper of dreams")
            monsters.append((boss, tile))

            self.create_entities(monsters, "monsters", populate_pool=number_of_monsters)

        if stairs and self.name == "cavern" + str(stairs.floor + 1):

            number_of_monsters = randint(self.width / 2 - 40, self.width / 2 - 20)
            # number_of_monsters = 0
            monsters = [("frog", get_tile("frog"))]

            self.create_entities(monsters, "monsters", populate_pool=number_of_monsters)

        if self.name == "dream":

            self.create_decor()
            number_of_monsters = randint(int(self.width / 4), int(self.width / 2))

            if self.owner.world_tendency < 0:
                monsters = get_fighters_by_attribute("chaos", True)
            elif self.owner.world_tendency > 0:
                monsters = get_fighters_by_attribute("light", True)
            else:
                monsters = get_fighters_by_attribute("neutral", True)
            monsters.sort()
            spawn_rates = self.owner.get_spawn_rates(monsters)

            monster_pool = choices(monsters, spawn_rates, k=number_of_monsters)

            self.create_entities(monster_pool, "monsters")

        self.tiles[player.x][player.y].add_entity(player)

    def create_door(self, room=None, state="open", tile=None, char=None,
                    name="door", color=None, random=False, x=None, y=None):

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
            tile = get_tile_object(name)
            char = get_tile(name, tile, state)
        if color is None:
            color = "dark amber"
        door_component = Openable(name, char, state)
        door = Entity(x, y, 1, color, name, tile=tile, char=char,
                      door=door_component, stand_on_messages=False)
        self.tiles[x][y].add_entity(door)
        self.tiles[x][y].is_door = True
        self.tiles[x][y].door = door_component

        if state == "open":
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
        else:
            self.tiles[x][y].blocked = True
            self.tiles[x][y].block_sight = True

        return door

    def create_decor(self):

        if self.owner.tileset == "ascii":
            return
        # Generate rocks & rubble on floor tiles
        decor_odds = 0.1
        decor_options = ["rocks", "flowers", "plants", "mushrooms"]
        decor_map = np.random.rand(self.height, self.width)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.is_blocked(x, y) and not self.tiles[x][y].occupied:

                    if decor_map[y, x] < decor_odds and len(self.tiles[x][y].layers) == 0:
                        name = choice(decor_options)
                        char = get_tile_variant(name)
                        color = get_color(name, mod=self.owner.world_tendency)
                        self.tiles[x][y].layers.append((char, color))
                        self.tiles[x][y].name = name

                    if self.owner.world_tendency < 0:
                        if randint(1, 4) >= self.tiles[x][y].seed and len(self.tiles[x][y].layers) == 0:
                            if abs(self.owner.world_tendency) * 33 > randint(1, 100):
                                name = "bones"
                                char = get_tile_variant(name)
                                color = get_color(name, mod=self.owner.world_tendency)
                                self.tiles[x][y].layers.append((char, color))
                                self.tiles[x][y].name = name

    def create_entities(self, pool=None, category=None, populate_pool=None, location=None):
        """
        Creates and adds entities to map from the given pool.
        :param pool: List of entities in format (name, char)
        :param category: Entity category, e.g. monsters, npcs, allies
        :param populate_pool: If number set, populates the pool with amount
        :param location: Tuple of coordinates to place entity, random if None
        """
        player = self.owner.player

        if populate_pool is not None:
            pool = choices(pool, k=populate_pool)

        for item in pool:
            if location is None:
                x = randint(1, self.width - 1)
                y = randint(1, self.height - 1)
                while self.is_blocked(x, y) or x == player.x and y == player.y:
                    x, y = randint(1, self.width -
                                   1), randint(1, self.height - 1)
            else:
                x, y = location[0], location[1]

            if not any([entity for entity in self.entities[category] if entity.x == x and entity.y == y]):
                name = item[0]
                char = item[1]
                f_data = self.owner.owner.data.fighters[name]
                color = get_color(name, f_data, self.owner.world_tendency)
                remarks = f_data["remarks"]
                npc_component = None
                dialogue_component = None
                fighter_component = Fighter(hp=f_data["hp"], ac=f_data["ac"], ev=f_data["ev"],
                                            atk=f_data["atk"], mv_spd=f_data["mv_spd"],
                                            atk_spd=f_data["atk_spd"], size=f_data["size"], fov=f_data["fov"])
                if "ai" in f_data.keys() and f_data["ai"] == "caster":
                    ai_component = AICaster()
                elif "ai" in f_data.keys() and f_data["ai"] == "npc":
                    ai_component = AIBasic(passive=True)
                    npc_component = Npc(name)
                else:
                    ai_component = AIBasic()
                if "dialogue" in f_data.keys() and f_data["dialogue"]:
                    dialogue_component = Dialogue(name)
                light_component = LightSource(radius=fighter_component.fov)
                status_effects_component = StatusEffects(name)
                animations_component = Animations()
                monster = Entity(x, y, 1,
                                 color, name,
                                 char=char,
                                 blocks=True, fighter=fighter_component, ai=ai_component,
                                 light_source=light_component,
                                 status_effects=status_effects_component, remarks=remarks,
                                 animations=animations_component, dialogue=dialogue_component, npc=npc_component)
                monster.abilities = Abilities(monster)
                monster.light_source.initialize_fov(self)
                if "xtra_info" in f_data.keys():
                    monster.xtra_info = f_data["xtra_info"]
                if category == "npcs":
                    monster.ai.ally = True
                    monster.indicator_color = "light green"
                if f_data["size"] == "gigantic":
                    monster.boss = True
                    monster.occupied_tiles = [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]

                self.tiles[x][y].add_entity(monster)
                self.entities[category].append(monster)


    @staticmethod
    def entity_at_coordinates(entities, x, y):
        result = []
        for category in entities:
            for entity in entities[category]:
                if entity.x == x and entity.y == y:
                    result.append(entity)
        return result
