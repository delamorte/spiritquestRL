from math import ceil
from random import choice, choices, randint

import numpy as np
from scipy.signal import convolve2d
from tcod.map import compute_fov

from components.entity import Entity
from components.item import Item
from components.openable import Openable
from components.stairs import Stairs
from components.wall import Wall
from data import json_data
from map_gen.algorithms.messy_bsp import MessyBSPTree
from map_gen.algorithms.room_addition import RoomAddition
from map_gen.tile import Tile
from map_gen.tilemap import get_tile, get_color, get_tile_by_value, get_tile_object, get_tile_variant


class GameMap:
    def __init__(self, width, height, name, biome=None, title=None, dungeon_level=0):
        self.algorithm = None
        self.owner = None
        self.entities = {
            "monsters": [],
            "objects": [],
            "decorations": [],
            "npcs": [],
            "player": [],
            "allies": [],
            "cursor": [],
        }
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
        radius = entity.fighter.fov

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
                        ground_top_tile = get_tile_object(name)
                        color = get_color(name, mod=self.owner.world_tendency)
                        top_tile = Entity(x, y,
                                          color, name, tile=ground_top_tile, char=ground_top_char)
                        self.add_entity(top_tile)

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
                            self.add_entity(door)
                            self.tiles[x][y].is_door = True
                            self.tiles[x][y].door = door_component
                            door_component.set_state(door_component.state, self)
                            entities.append(door)
                        elif tile["interactable"] or tile["pickable"]:
                            item_component = Item(name, pickable=tile["pickable"], interactable=tile["interactable"],
                                                  light_source=tile["light_source"])
                            item = Entity(x, y,
                                          color, name, tile=tile, item=item_component)
                            if item.name == "flask":  # For testing "reveal" skill
                                item.hidden = True
                            self.add_entity(item)
                            item_component.set_attributes(self)
                            entities.append(item)
                        elif tile["stairs"]:
                            stairs_component = Stairs(("hub", x, y), ["dream"], name)
                            portal = Entity(x, y, color, name, tile=tile,
                                            stairs=stairs_component)
                            self.add_entity(portal)
                            stairs_component.set_attributes(self)
                            portal.xtra_info = "Meditate and go to dream world with '<' or '>'"
                            entities.append(portal)
                        else:
                            wall_component = Wall(name=name, tile=tile)
                            wall = Entity(x, y,
                                          color, name, char=char, tile=tile, wall=wall_component)
                            self.add_entity(wall)
                            wall_component.set_attributes(self)
                            entities.append(wall)

                else:
                    # Horizontal walls
                    if (y == room.y1 or y == room.y2 - 1) and 0 <= x <= room.x2 - 1:
                        wall = self.create_wall(room.wall_type, x, y, 0)
                        entities.append(wall)
                    # Vertical walls
                    elif (x == room.x1 or x == room.x2 - 1) and 0 <= y < room.y2 - 1:
                        wall = self.create_wall(room.wall_type, x, y, 2)
                        entities.append(wall)
                    # Upper right corner
                    elif x == room.x2 and y == room.y1:
                        wall = self.create_wall(room.wall_type, x, y, 1)
                        entities.append(wall)
                    # Lower right corner
                    elif x == room.x2 and y == room.y2:
                        wall = self.create_wall(room.wall_type, x, y, 3)
                        entities.append(wall)
                    # Lower left corner
                    elif x == room.x1 and y == room.y2:
                        wall = self.create_wall(room.wall_type, x, y, 5)
                        entities.append(wall)
                    # Upper left corner
                    elif x == room.x1 and y == room.y1:
                        wall = self.create_wall(room.wall_type, x, y, 7)
                        entities.append(wall)

                    else:
                        self.tiles[x][y].color = get_color(room.floor_type)
                        self.tiles[x][y].char = get_tile(room.floor_type)
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
        self.add_entity(wall)
        wall_component.set_attributes(self)
        return wall

    def generate_map(self, name=None, algorithm=None):

        # generators = {
        #               "random_walk": DrunkardsWalk(self.width, self.height),
        #               "messy_bsp": MessyBSPTree(self.width, self.height),
        #               "cellular": CellularAutomata(self.width, self.height),
        #               "room_addition": RoomAddition(self.width, self.height)
        #             }

        generators = {
            "messy_bsp": MessyBSPTree(self.width, self.height),
            "drunkard": RoomAddition(self.width, self.height, drunkard=True),
            "cellular": RoomAddition(self.width, self.height, only_cellular=True),
            "room_addition": RoomAddition(self.width, self.height),
            "vaults": RoomAddition(self.width, self.height, only_vaults=True),
            "squares": RoomAddition(self.width, self.height, only_squares=True),
            "squares_and_crosses": RoomAddition(self.width, self.height, squares_and_crosses=True),
        }

        if algorithm:
            map_algorithm = algorithm
        elif name == "hub":
            map_algorithm = RoomAddition(self.width, self.height, drunkard=True, only_squares=1, build_later=True,
                                         first_room_max_size=8)
        elif not name:
            map_algorithm = choice(list(generators.values()))
        else:
            map_algorithm = generators[name]

        self.algorithm = map_algorithm
        map_algorithm.generate_level()

        floor_name = self.biome.biome_data["floor"]
        wall_name = self.biome.biome_data["wall"]
        floor_tile = get_tile(floor_name)
        wall_tile = get_tile(wall_name)
        wall_tile_object = get_tile_object(wall_name)
        modifier = self.biome.biome_modifier
        floor_color = get_color(floor_name)
        wall_color = get_color(wall_name, mod=modifier)
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.tiles[x][y].color = floor_color
                self.tiles[x][y].char = floor_tile
                if map_algorithm.level[y][x] == 1:
                    self.tiles[x][y].spawnable = False
                    wall = Entity(x, y, wall_color, wall_name, tile=wall_tile_object,
                                  char=wall_tile)
                    if wall.wall:
                        wall.wall.set_attributes(self)
                    self.add_entity(wall)

                else:
                    self.tiles[x][y].spawnable = True

        # debug
        # for room in self.algorithm.rooms:
        #     walls = room.inner
        #     for tile in walls:
        #         x, y = tile[0], tile[1]
        #         for entity in self.tiles[x][y].entities_on_tile:
        #             entity.color = "red"

    def process_rooms(self):

        for room in self.algorithm.rooms:
            if self.biome.biome_data["name"] == "hub" and not self.biome.home:
                feature_name = "Shaman's Retreat"
                self.biome.home = feature_name
                room.lightness = 0.8
                room.build_later = False
            elif room.build_later:
                continue
            else:
                feature_name = choice(self.biome.features)
            feature_data = json_data.data.biome_features[feature_name]
            room.feature = feature_name
            if feature_data["has_door"]:
                room.has_door = True
            wall_name = choice(feature_data["wall"])
            wall_tile = get_tile_object(wall_name)
            wall_color = get_color(wall_name)
            floor_name = choice(feature_data["floor"])
            if "floor_colors" in feature_data.keys():
                floor_color = choice(feature_data["floor_colors"])
            else:
                floor_color = get_color(floor_name)
            floor_tile = get_tile(floor_name)
            room.floor_type = floor_name
            room.wall_type = wall_name
            for tile in room.inner:
                x, y = tile[0], tile[1]
                self.tiles[x][y].room_id = room.id_nr
                self.tiles[x][y].natural_light_level = room.lightness
                if self.tiles[x][y].entities_on_tile:
                    for entity in self.tiles[x][y].entities_on_tile:
                        self.remove_entity(entity)

                self.tiles[x][y].char = floor_tile
                self.tiles[x][y].color = floor_color

            for tile in room.outer:
                x, y = tile[0], tile[1]
                self.tiles[x][y].room_id = room.id_nr
                if wall_tile["draw_floor"]:
                    self.tiles[x][y].char = floor_tile
                    self.tiles[x][y].color = floor_color
                self.tiles[x][y].natural_light_level = room.lightness
                if self.tiles[x][y].entities_on_tile:
                    for entity in self.tiles[x][y].entities_on_tile:
                        self.remove_entity(entity)
                char = get_tile(wall_name)
                wall = Entity(x, y, wall_color, wall_name, tile=wall_tile, char=char)
                if wall.wall:
                    wall.wall.set_attributes(self)
                self.add_entity(wall)

        for room in self.algorithm.rooms:
            tunnels = room.tunnel
            entrances = room.entrances

            for tile in tunnels:
                x, y = tile[0], tile[1]
                if self.tiles[x][y].room_id is not None:
                    continue
                floor_name = room.floor_type
                floor_color = room.floor_color
                floor_tile = get_tile(floor_name)
                self.tiles[x][y].char = floor_tile
                self.tiles[x][y].color = floor_color
                if self.tiles[x][y].entities_on_tile and tile not in room.outer and tile not in entrances:
                    for entity in self.tiles[x][y].entities_on_tile:
                        self.remove_entity(entity)
            for tile in entrances:
                x, y = tile[0], tile[1]
                if self.tiles[x][y].entities_on_tile:
                    for entity in self.tiles[x][y].entities_on_tile:
                        self.remove_entity(entity)
                if room.has_door:
                    if self.biome.home == "Shaman's Retreat":
                        state = "locked"
                    else:
                        state = "closed"
                    self.create_door(state=state, x=x, y=y)
                    break

            for tile in room.outer:
                x, y = tile[0], tile[1]
                wall_name = room.wall_type
                wall_tile = get_tile_object(wall_name)
                if wall_tile["corners"]:
                    facing = self.get_tile_direction(x, y)
                    if not facing:
                        continue
                    char = get_tile_variant(name=wall_name, facing=facing)
                    if self.tiles[x][y].entities_on_tile:
                        for entity in self.tiles[x][y].entities_on_tile:
                            if entity.name == wall_name:
                                entity.char = char

        self.create_entities_in_rooms()

    def process_prefabs(self):
        if self.biome.biome_data["name"] == "hub":
            for room in self.algorithm.rooms:
                if room.feature == "Shaman's Retreat":
                    self.biome.home = room
                    break
            x, y = choice(list(self.biome.home.inner))
            while self.tiles[x][y].blocking_entity:
                x, y = choice(list(self.biome.home.inner))
            name = "holy symbol"
            portal = get_tile_object(name)
            color = get_color(name)
            stairs_component = Stairs(("hub", x, y), ["dream"], name)
            portal = Entity(x, y, color, name, tile=portal,
                            stairs=stairs_component)
            self.add_entity(portal)
            portal.xtra_info = "Meditate and go to dream world with '<' or '>'"

    def add_entity(self, entity):
        if entity not in self.tiles[entity.x][entity.y].entities_on_tile:
            self.tiles[entity.x][entity.y].add_entity(entity)
        if entity not in self.entities[entity.category]:
            self.entities[entity.category].append(entity)

    def remove_entity(self, entity):
        if entity in self.tiles[entity.x][entity.y].entities_on_tile:
            self.tiles[entity.x][entity.y].remove_entity(entity)
        if entity in self.entities[entity.category]:
            self.entities[entity.category].remove(entity)

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
                        self.add_entity(wall)
                        wall_component.set_attributes(self)
                        entities.append(wall)

        return entities

    def is_blocked(self, x, y):

        if x >= self.width - 1 or x <= 0 or y >= self.height - 1 or y <= 0:
            return True
        elif self.tiles[x][y].blocked:
            return True
        elif self.tiles[x][y].blocking_entity and not self.tiles[x][y].blocking_entity.fighter:
            return True

        return False

    def place_player(self):
        # Place player
        player = self.owner.player
        px, py = 0, 0
        if self.biome.biome_data["name"] == "hub":
            px, py = choice(list(self.biome.home.inner))
            while self.tiles[px][py].blocking_entity:
                px, py = choice(list(self.biome.home.inner))
        if self.name == "dream":
            px, py = randint(1, self.width - 1), \
                randint(1, self.height - 1)

            while not self.tiles[px][py].spawnable:
                #    while self.is_blocked(px, py):
                px, py = randint(1, self.width - 1), \
                    randint(1, self.height - 1)
        player.x, player.y = px, py

        self.entities["player"] = [player]
        self.add_entity(player)

    def init_light_sources(self):
        for category, entities in self.entities.items():
            for entity in entities:
                if entity.light_source:
                    entity.light_source.initialize_fov(self)

    def create_door(self, room=None, state="open", tile=None, char=None,
                    name="door", color=None, x=None, y=None):

        """
        Create a door entity in map. If no coordinates are given,
        pick a random (x, y) from room walls.
        If any of the room walls are against the map border,
        make sure that door cannot be placed there.
        """

        if not x or not y:
            locations = list(room.outer)
            x, y = choice(locations)
            if self.tiles[x][y].entities_on_tile:
                for entity in self.tiles[x][y].entities_on_tile:
                    self.remove_entity(entity)

        if tile is None:
            tile = get_tile_object(name)
            char = get_tile(name, tile, state)
        if color is None:
            color = "dark amber"
        door = Entity(x, y, color, name, tile=tile, char=char,
                      stand_on_messages=False)
        door.door.set_state(state, game_map=self)
        self.add_entity(door)

        return door

    def create_entities_in_rooms(self):
        """
        Creates and adds monsters to all rooms in the map from the given pool.
        """
        for room in self.algorithm.rooms:
            if room.build_later:
                continue
            entity_count = 0
            feature_data = json_data.data.biome_features[room.feature]
            room_entities = feature_data["entities"]

            if "windows" in feature_data.keys() and feature_data["windows"]:
                entity_name = "window"
                nr_of_entities_to_place = self.get_room_population(room.size, "windows")
                locations = list(room.outer)
                tile = get_tile_object(entity_name)
                color = get_color(entity_name)
                for _ in nr_of_entities_to_place:
                    x, y = choice(locations)
                    if self.tiles[x][y].entities_on_tile:
                        for remove_entity in self.tiles[x][y].entities_on_tile:
                            self.remove_entity(remove_entity)
                    entity = Entity(x, y, color, entity_name, tile, category="objects")

                    self.add_entity(entity)

            for category, entities in room_entities.items():
                if not entities:
                    continue
                if not self.biome.biome_data["monsters"] and category == "monsters":
                    continue
                if entity_count >= room.max_entities:
                    break
                nr_of_entities_to_place, areas = self.get_room_population(room.size, category)
                if category == "decorations":
                    self.place_decorations(areas, entities, room)
                    continue
                else:
                    entities_to_place = choices(entities, k=nr_of_entities_to_place)

                for entity_name in entities_to_place:
                    if entity_count >= room.max_entities:
                        break
                    # Choose random empty location in room
                    if category == "monsters" and room.floor_type == "water" and not room.wall_type == "water":
                        inner = list(room.inner)
                        outer = list(room.outer)
                        locations = inner + outer
                    else:
                        locations = list(room.inner)
                    x, y = choice(locations)
                    if category == "objects":
                        while self.tiles[x][y].entities_on_tile:
                            x, y = choice(locations)
                    else:
                        while self.tiles[x][y].blocking_entity or self.tiles[x][y].blocked:
                            x, y = choice(locations)

                    tile = get_tile_object(entity_name)
                    color = get_color(entity_name, mod=self.owner.world_tendency)
                    entity = Entity(x, y, color, entity_name, tile, category=category)
                    self.add_entity(entity)
                    entity_count += 1

    def get_tile_direction(self, x, y):
        # Define the neighboring tile positions in the cardinal directions
        directions_idx_map = {
            "north": 0,
            "south": 4,
            "west": 6,
            "east": 2,
            "northwest": 7,
            "northeast": 1,
            "southwest": 5,
            "southeast": 3
        }

        neighbors = get_cornering_tiles(x, y, self.tiles, pattern="8bit", masked=True)

        # Determine and return the correct facing based on the neighboring tiles
        if neighbors[1] and neighbors[6] and not neighbors[4]:
            return directions_idx_map["north"]
        elif neighbors[3] and neighbors[4] and not neighbors[1]:
            return directions_idx_map["east"]
        elif neighbors[1] and neighbors[6] and not neighbors[3]:
            return directions_idx_map["south"]
        elif neighbors[3] and neighbors[4] and not neighbors[6]:
            return directions_idx_map["west"]

        elif neighbors[4] and neighbors[6] and not neighbors[7]:
            return directions_idx_map["northwest"]
        elif neighbors[1] and neighbors[4] and not neighbors[2]:
            return directions_idx_map["northeast"]
        elif neighbors[1] and neighbors[3] and not neighbors[0]:
            return directions_idx_map["southeast"]
        elif neighbors[3] and neighbors[6] and not neighbors[5]:
            return directions_idx_map["southwest"]

        elif neighbors[4] and neighbors[6] and not neighbors[1] and not neighbors[3]:
            return directions_idx_map["northwest"]
        elif neighbors[1] and neighbors[4] and not neighbors[3] and not neighbors[6]:
            return directions_idx_map["northeast"]
        elif neighbors[3] and neighbors[6] and not neighbors[1] and not neighbors[4]:
            return directions_idx_map["southwest"]
        elif neighbors[1] and neighbors[3] and not neighbors[4] and not neighbors[6]:
            return directions_idx_map["southeast"]
        elif neighbors[4] and not neighbors[1] and not neighbors[3] and not neighbors[6]:
            return directions_idx_map["east"]

        return None

    def get_room_population(self, room_size, category):
        decorations = None
        entities_count = 1
        if category == "monsters":
            entities_count = int(ceil(room_size / 50) * randint(1, 3)) - 1
        elif category == "npcs":
            entities_count = 1
        elif category == "allies":
            entities_count = 1
        elif category == "objects":
            entities_count = randint(1, 3)
        elif category == "windows":
            entities_count = room_size / 10
        elif category == "decorations":
            decorations, entities_count = self.get_decorations(room_size)

        return entities_count, decorations

    def place_decorations(self, areas, entities, room):
        while areas:
            entity_name = choice(entities)

            area = areas.pop()
            locations = list(room.inner)
            x, y = choice(locations)
            counter = 0
            while self.tiles[x][y].blocking_entity or self.tiles[x][y].blocked or np.count_nonzero(
                    self.algorithm.level[y:y + area.shape[0], x:x + area.shape[1]]) > 0 or counter > 10:
                x, y = choice(locations)
                counter += 1

            tile = get_tile_object(entity_name)
            color = get_color(entity_name, mod=self.owner.world_tendency)
            for i, x2 in enumerate(range(x, x + len(area[1]))):
                for j, y2 in enumerate(range(y, y + len(area[0]))):
                    if area[j][i] == 0:
                        entity = Entity(x2, y2, color, entity_name, tile, category="decorations")
                        if entity.wall:
                            entity.wall.set_attributes(self)
                        self.add_entity(entity)

        return

    @staticmethod
    def get_decorations(room_size):
        entities_count = 0
        decorations = []
        nr_of_decorations = int(room_size / 10)
        for _ in range(nr_of_decorations + 1):
            rng = np.random.default_rng()
            arr = rng.choice(2, (2, 2), p=[0.2, 0.8])
            decorations.append(arr)
            entities_count += np.count_nonzero(arr)
        return decorations, entities_count

    @staticmethod
    def entity_at_coordinates(entities, x, y):
        result = []
        for category in entities:
            for entity in entities[category]:
                if entity.x == x and entity.y == y:
                    result.append(entity)
        return result


def get_cornering_tiles(x, y, tiles, radius=1, pattern="4bit", masked=False):
    patterns_map = {
        "4bit": [[0, 1, 0],
                 [1, 0, 1],
                 [0, 1, 0]],
        "8bit": [[1, 1, 1],
                 [1, 0, 1],
                 [1, 1, 1]],
        "corners": [[1, 0, 1],
                    [0, 0, 0],
                    [1, 0, 1]]
    }
    kernel = patterns_map[pattern]
    if radius > 1:
        kernel = np.pad(kernel, radius - 1, mode='edge')
    mask = np.zeros_like(tiles, dtype=bool)  # build empty mask
    mask[x, y] = True  # set target(s)

    # boolean indexing
    neighbours = tiles[convolve2d(mask, kernel, mode='same').astype(bool)]
    neighbours_masked = [1 if x.blocked else 0 for x in neighbours]
    if masked:
        return neighbours_masked
    return neighbours
