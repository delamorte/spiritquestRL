from math import sqrt
from random import randint, choice

import numpy as np
import tcod

from components.animation import Animation
from data import json_data
from game_states import GameStates
from helpers import get_article
from map_objects import tilemap
from ui.message import Message


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, layer, char, color, name, blocks=False, player=None,
                 fighter=None, ai=None, item=None, inventory=None, stairs=None, summoner=None,
                 wall=None, door=None, cursor=None, light_source=None, abilities=None,
                 status_effects=None, stand_on_messages=True, boss=False, hidden=False, remarks=None,
                 indicator_color="dark red", animations=None, visible=False):
        self.x = x
        self.y = y
        self.layer = layer
        self.char = char
        if color is None:
            color = "default"
        self.color = color
        self.name = name
        self.colored_name = "[color={0}]{1}[color=default]".format(color, name.capitalize())
        self.blocks = blocks
        self.fighter = fighter
        self.summoner = summoner
        self.player = player
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.xtra_info = None
        self.wall = wall
        self.door = door
        self.cursor = cursor
        self.last_seen_x = x
        self.last_seen_y = y
        self.light_source = light_source
        self.abilities = abilities
        self.status_effects = status_effects
        self.stand_on_messages = stand_on_messages
        self.occupied_tiles = None  # For entities bigger than 1 tile
        self.boss = boss
        self.hidden = hidden
        self.remarks = remarks
        self.indicator_color = indicator_color
        self.animations = animations
        self.dead = False
        self.visible = visible

        # Set entity as component owner, so components can call their owner
        if self.player:
            self.player.owner = self

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.wall:
            self.wall.owner = self

        if self.door:
            self.door.owner = self

        if self.cursor:
            self.cursor.owner = self

        if self.light_source:
            self.light_source.owner = self

        if self.abilities:
            self.abilities.owner = self

        if self.status_effects:
            self.status_effects.owner = self

        if self.summoner:
            self.summoner.owner = self

        if self.animations:
            self.animations.owner = self

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, escape=False):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if escape:
            dx = -1 * dx
            dy = -1 * dy

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                game_map.tiles[self.x+dx][self.y+dy].blocking_entity):
            self.move(dx, dy)

    def move_to_tile(self, game_map, x, y):
        if not (game_map.is_blocked(x, y) or
                game_map.tiles[x][y].blocking_entity):
            self.x = x
            self.y = y

    def get_path_to(self, target, entities, game_map):
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        walkable = np.frompyfunc(lambda tile: not tile.blocked, 1, 1)
        cost = np.array(walkable(game_map.tiles), dtype=np.int8)

        blocking_entities = entities["monsters"] + entities["allies"] + entities["player"]

        for entity in blocking_entities:
            # Check that an entity blocks movement and the cost isn't zero (blocking.)
            if entity.blocks and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.x, self.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path = list(pathfinder.path_to((target.x, target.y))[1:])

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(int(index[0]), int(index[1])) for index in path]

    def distance_to(self, other):
        # Use Chebysev distance
        if self.occupied_tiles is not None:
            return min(max(abs(other.x - self.x), abs(other.y - self.y)),
                       max(abs(other.x - (self.x + 1)), abs(other.y - self.y)),
                       max(abs(other.x - self.x), abs(other.y - (self.y + 1))),
                       max(abs(other.x - (self.x + 1)), abs(other.y - (self.y + 1))))
        else:
            return max(abs(other.x - self.x), abs(other.y - self.y))

    def kill(self):
        if self.player:
            self.char = tilemap.data.tiles["player_remains"]
            death_message = Message(msg="You died!", style="death")
            self.dead = True

        elif self.ai.ally:
            self.light_source = None
            self.blocks = False
            self.fighter = None
            self.ai = None
            self.dead = True
            return None

        else:
            death_message = Message("The {0} is dead!".format(self.name), style="death")

            if self.boss:
                self.char = tilemap.data.tiles["boss_remains"]
                self.color = "darkest red"
            else:
                self.char = tilemap.data.tiles["monster_remains"]
                self.color = "dark gray"
                self.light_source = None
            self.blocks = False
            self.fighter = None
            self.ai = None
            self.dead = True
            self.name = "remains of " + get_article(self.name) + " " + self.name
            self.layer = 1

        return death_message

    def remark(self, random=True, sneak=False, game_map=None):
        if self.x > game_map.width - 5 or self.x < 5:
            return
        if self.animations.buffer:
            return
        if sneak:
            remark = choice(json_data.data.remarks["sneaking"])
        elif self.remarks:
            remark = choice(self.remarks)
        else:
            return
        chance = randint(0, 6) if random else 0
        if chance == 0:
            self.animations.buffer.append(Animation(self, self, dialog=remark, target_self=True))
