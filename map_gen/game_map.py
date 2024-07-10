import random
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
from map_gen.algorithms.room_addition import RoomAddition
from map_gen.tile import Tile
from map_gen.tilemap import get_tile, get_color, get_tile_by_value, get_tile_object, get_tile_variant


class GameMap:
    def __init__(self, width, height, name, biome=None, title=None, dungeon_level=0):
        self.player_start_room = None
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
                       algorithm="square", empty_tiles=False, exclude_player=False, only_visible=True):
        """
        :param only_visible: return only neighbours who are in visible radius
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
                    if not include_self and tile.x == entity.x and tile.y == entity.y:
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
            if only_visible:
                return list(filter(lambda tile: self.visible[tile.x, tile.y], tiles))
            else:
                return tiles
        else:
            if only_visible:
                return list(filter(lambda entity: self.visible[entity.x, entity.y], entities))
            else:
                return entities

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
            # "messy_bsp": MessyBSPTree(self.width, self.height),
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

        print("processing rooms..")
        for room in self.algorithm.feature_rooms:
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
            room.feature_name = feature_name
            room.parent_room.feature_name = feature_name
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
            room.floor_color = floor_color
            for tile in room.tiles:
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
                if tile in room.entrances:
                    continue
                if self.algorithm.level[y][x] == 0:
                    if tile in room.borders:
                        room.entrances.add(tile)
                    else:
                        continue
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
                self.tiles[x][y].spawnable = False

        # self.connect_caves()
        # self.algorithm.connect_caves()
        # print("find isolated rooms")
        # isolated_rooms = self.algorithm.get_rooms_by_flood_fill(prefab=False)
        # if isolated_rooms:
        #     for isolated_room in isolated_rooms:
        #         #closest_room = self.algorithm.get_closest_room(isolated_room)
        #         #self.algorithm.connect_vault_to_nearest(isolated_room, closest_room)
        #
        #         for tile in isolated_room.inner:
        #             x, y = tile[0], tile[1]
        #             if x >= self.width or y >= self.height:
        #                 continue
        #             self.tiles[x][y].color = "purple"
        #
        #         for tile in isolated_room.outer:
        #             x, y = tile[0], tile[1]
        #             if x >= self.width or y >= self.height:
        #                 continue
        #             self.tiles[x][y].color = "blue"

        # print("connect isolated rooms")
        # self.algorithm.connect_caves(connect_features=True, isolated_rooms=isolated_rooms)
        # print("make sure all rooms are traversible")
        # self.algorithm.connect_rooms()

        print("creating footprints and adjusting wall corners..")
        for room in self.algorithm.feature_rooms:
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

            tunnels = room.tunnel

            if "trail" not in self.biome.biome_data.keys():
                continue

            trail_name = choice(self.biome.biome_data["trail"])
            trail_color = get_color(trail_name)
            trail_tile = get_tile_object(trail_name)

            for tile in tunnels:
                if tile not in self.algorithm.all_feature_tiles:
                    x, y = tile[0], tile[1]
                    # create trail
                    create_steps = random.random()
                    if create_steps > 0.5:
                        entity = Entity(x, y, trail_color, trail_name, trail_tile, category="decorations")
                        self.add_entity(entity)

        print("room processed")
        self.create_entities_in_rooms()

    def process_prefabs(self):
        if self.biome.biome_data["name"] == "hub":
            for room in self.algorithm.feature_rooms:
                if room.feature_name == "Shaman's Retreat":
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
            locations = self.biome.home.inner
            spawnable_locations = [(x, y) for (x, y) in locations if self.tiles[x][y].spawnable]
            px, py = choice(spawnable_locations)

            # DEBUG
            self.place_quest_npc(debug=True)
        if self.name == "dream":
            start_room = choice(self.algorithm.rooms)
            self.player_start_room = start_room
            locations = start_room.outer
            spawnable_locations = [(x, y) for (x, y) in locations if self.tiles[x][y].spawnable]
            px, py = choice(spawnable_locations)

        player.x, player.y = px, py

        self.entities["player"] = [player]
        self.add_entity(player)

    def place_quest_npc(self, debug=False):
        if debug:
            npc = "blacksmith"
        else:
            npc = self.biome.quest_npc
        if not npc:
            return
        if debug:
            npc_room = self.biome.home
        else:
            npc_rooms = [room for room in self.algorithm.feature_rooms if npc in room.feature_name.lower()]
            if not npc_rooms:
                npc_room = self.algorithm.get_closest_or_furthest_room(self.player_start_room, closest=False)
            else:
                npc_room = self.algorithm.get_closest_or_furthest_room(self.player_start_room, rooms=npc_rooms,
                                                                       closest=False)
        locations = npc_room.inner
        spawnable_locations = [(x, y) for (x, y) in locations if
                               self.tiles[x][y].spawnable and not self.tiles[x][y].blocked]

        x, y = choice(spawnable_locations)

        tile = get_tile_object(npc)
        color = get_color(npc, mod=self.owner.world_tendency)
        entity = Entity(x, y, color, npc, tile, category="npcs")
        self.add_entity(entity)

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
            if not room.feature_name:
                continue
            feature_data = json_data.data.biome_features[room.feature_name]
            room_entities = feature_data["entities"]

            # if "windows" in feature_data.keys() and feature_data["windows"] and room.feature_room:
            #     feature_room = room.feature_room
            #     entity_name = "window"
            #     nr_of_entities_to_place = self.get_room_population(room, "windows")
            #     locations = list(feature_room.outer)
            #     tile = get_tile_object(entity_name)
            #     color = get_color(entity_name)
            #     if not locations:
            #         continue
            #     for _ in nr_of_entities_to_place:
            #         x, y = choice(locations)
            #         if self.tiles[x][y].entities_on_tile:
            #             for remove_entity in self.tiles[x][y].entities_on_tile:
            #                 self.remove_entity(remove_entity)
            #         entity = Entity(x, y, color, entity_name, tile, category="objects")
            #
            #         self.add_entity(entity)
            print("placing entities")
            for category, entities in room_entities.items():

                if category == "windows":
                    continue
                if not entities:
                    continue
                if not self.biome.biome_data["monsters"] and category == "monsters":
                    continue
                if entity_count >= room.max_entities:
                    break
                nr_of_entities_to_place = self.get_room_population(room, category)
                entities_to_place = choices(entities, k=nr_of_entities_to_place)

                # Get spawnable locations
                if category == "monsters" and room.floor_type == "water" and not room.wall_type == "water":
                    inner = room.inner
                    outer = room.outer
                    locations = inner + outer
                else:
                    if room.feature_room and category == "objects":
                        locations = room.feature_room.inner
                    else:
                        if room.feature_room:
                            locations = room.inner.difference(room.feature_room.outer)
                        else:
                            locations = room.inner

                spawnable_locations = [(x, y) for (x, y) in locations if self.tiles[x][y].spawnable]

                for entity_name in entities_to_place:
                    if entity_count >= room.max_entities or len(spawnable_locations) == 0:
                        break

                    # Choose a random spawnable location
                    x, y = choice(spawnable_locations)

                    tile = get_tile_object(entity_name)
                    color = get_color(entity_name, mod=self.owner.world_tendency)
                    entity = Entity(x, y, color, entity_name, tile, category=category)
                    self.add_entity(entity)
                    entity_count += 1

        print("clearing entrances")

        doors = set()
        for room in self.algorithm.feature_rooms:
            entrances = room.entrances
            for tile in entrances:
                x, y = tile[0], tile[1]
                # self.tiles[x][y].color = "pink"
                self.tiles[x][y].char = get_tile(room.floor_type)
                self.tiles[x][y].color = get_color(room.floor_type)

                if self.tiles[x][y].entities_on_tile:
                    for entity in self.tiles[x][y].entities_on_tile:
                        self.remove_entity(entity)

                if room.has_door:
                    if self.biome.home == "Shaman's Retreat":
                        state = "locked"
                    else:
                        state = "closed"

                    doors.add(self.create_door(state=state, x=x, y=y))

        # Scan for doors and remove 1-tile adjacent ones
        for door in doors:
            neighbours = self.get_neighbours(door, only_visible=False)
            if neighbours:
                if len(neighbours) >= 5:
                    self.remove_entity(door)
                    continue
                for neighbour in neighbours:
                    if neighbour.door:
                        self.remove_entity(door)

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

    def get_room_population(self, room, category):
        entities_count = 1
        room_size = room.feature_room.size
        if category == "monsters":
            room_size = room.size
            entities_count = int(ceil(room_size / 50) * randint(1, 3)) - 1
        elif category == "npcs":
            entities_count = 1
        elif category == "allies":
            entities_count = 1
        elif category == "objects":
            # entities_count = randint(1, 3)
            # decorations, entities_count = self.get_decorations(room_size)
            entities_count = randint(1, max(2, int(room_size / 10)))
        elif category == "windows":
            entities_count = room_size / 10
        elif category == "decorations":
            room_size = room.size
            entities_count = randint(5, max(6, int(room_size / 10)))

        return entities_count

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
