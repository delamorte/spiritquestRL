from math import sqrt
from random import randint, choice

import numpy as np
import tcod

from components.AI.ai_basic import AIBasic
from components.AI.ai_caster import AICaster
from components.abilities import Abilities
from components.animation import Animation
from components.animations import Animations
from components.dialogue import Dialogue
from components.fighter import Fighter
from components.inventory import Inventory
from components.item import Item
from components.light_source import LightSource
from components.npc import Npc
from components.openable import Openable
from components.player import Player
from components.status_effects import StatusEffects
from components.wall import Wall
from data import json_data
from helpers import get_article
from map_gen.tilemap import get_tile, get_tile_variant, get_tile_object
from ui.message import Message


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, color, name, tile=None, layer=1, char=None, blocks=False, player=None,
                 fighter=None, ai=None, interactable=None, pickable=None, openable=None,
                 item=None, inventory=None, stairs=None, summoner=None, category="objects",
                 wall=None, door=None, cursor=None, light_source=None, abilities=None,
                 status_effects=None, stand_on_messages=True, boss=False, hidden=False, remarks=None,
                 indicator_color="dark red", animations=None, visible=False, dialogue=None, npc=None):
        """
        :param x:
        :param y:
        :param layer:
        :param color:
        :param name:
        :param tile:
        :param char:
        :param blocks:
        :param player:
        :param fighter:
        :param ai:
        :param interactable:
        :param pickable:
        :param openable:
        :param item:
        :param inventory:
        :param stairs:
        :param summoner:
        :param category: monsters, allies, npcs, objects, player, cursor
        :param wall:
        :param door:
        :param cursor:
        :param light_source:
        :param abilities:
        :param status_effects:
        :param stand_on_messages:
        :param boss:
        :param hidden:
        :param remarks:
        :param indicator_color:
        :param animations:
        :param visible:
        :param dialogue:
        :param npc:
        """
        self.x = x
        self.y = y
        self.layer = layer
        if not color:
            color = "default"
        self.color = color
        self.name = name
        if not tile:
            tile = get_tile_object(name)
        self.tile = tile
        if not char:
            if "tile_variants" in tile.keys():
                char = get_tile_variant(name)
            else:
                char = get_tile(name, tile)
        self.char = char
        self.colored_name = "[color={0}]{1}[color=default]".format(color, name.capitalize())
        self.blocks = blocks
        self.fighter = fighter
        self.summoner = summoner
        self.player = player
        self.category = category
        self.ai = ai
        self.interactable = interactable
        self.pickable = pickable
        self.openable = openable
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
        self.dialogue = dialogue
        self.npc = npc
        self.dead = False
        self.visible = visible
        self.light = tile["light"] if tile else True
        self.neutral = tile["neutral"] if tile else True
        self.chaos = tile["chaos"] if tile else True

        if self.category == "monsters" or self.category == "npcs" or self.category == "player":
            self.set_fighter_components()
        elif self.category == "objects":
            self.set_object_components()

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
            inventory_component = Inventory()
            self.inventory = inventory_component
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.blocks and not self.fighter:
            wall_component = Wall(name=name, tile=tile)
            self.wall = wall_component
            self.wall.owner = self

        if self.openable:
            door_component = Openable(name, self.char)
            self.door = door_component
            self.door.owner = self

        if self.interactable or self.pickable:
            item_component = Item(name, pickable=self.tile["pickable"], interactable=self.tile["interactable"],
                                  light_source=self.tile["light_source"])
            self.item = item_component
            self.item.owner = self

        if self.cursor:
            self.cursor.owner = self

        if self.light_source:
            light_component = LightSource(name=self.name, light_walls=False)
            if self.fighter:
                light_component.radius = self.fighter.fov
            self.light_source = light_component
            self.light_source.owner = self

        if self.abilities:
            self.abilities = Abilities(self)
            self.abilities.owner = self

        if self.status_effects:
            self.status_effects.owner = self

        if self.summoner:
            self.summoner.owner = self

        if self.animations:
            self.animations.owner = self

        if self.dialogue:
            self.dialogue.owner = self

        if self.npc:
            self.npc.owner = self

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
                game_map.tiles[self.x + dx][self.y + dy].blocking_entity):
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
                self.color = "darkest red"
            else:
                self.color = "dark gray"

            self.light_source = None
            self.blocks = False
            self.fighter = None
            self.ai = None
            self.dead = True
            self.name = "remains of " + get_article(self.name) + " " + self.name
            self.layer = 1

        return death_message

    def remark(self, chance=10, sneak=False, game_map=None):
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
        if chance >= (100 - randint(0, 100)):
            self.animations.buffer.append(Animation(self, self, dialog=remark, target_self=True))

    def set_fighter_components(self):
        f_data = json_data.data.fighters[self.name]
        fighter_component = Fighter(hp=f_data["hp"], ac=f_data["ac"], ev=f_data["ev"],
                                    atk=f_data["atk"], mv_spd=f_data["mv_spd"],
                                    atk_spd=f_data["atk_spd"], size=f_data["size"], fov=f_data["fov"])
        self.fighter = fighter_component
        self.remarks = f_data["remarks"]

        npc_component = None
        dialogue_component = None
        status_effects_component = StatusEffects(self.name)
        animations_component = Animations()

        if "ai" in f_data.keys() and f_data["ai"] == "caster":
            ai_component = AICaster()
        elif "ai" in f_data.keys() and f_data["ai"] == "npc":
            ai_component = AIBasic(passive=True)
            npc_component = Npc(self.name)
        elif self.category == "allies":
            self.indicator_color = "light green"
            self.name += " (friend)"
            ai_component = AIBasic(ally=True)
        else:
            ai_component = AIBasic()

        if "dialogue" in f_data.keys() and f_data["dialogue"]:
            dialogue_component = Dialogue(self.name)

        self.ai = ai_component
        if npc_component:
            self.npc = npc_component
        if dialogue_component:
            self.dialogue = dialogue_component

        self.status_effects = status_effects_component
        self.animations = animations_component
        self.light_source = True
        self.blocks = True
        self.abilities = True

        if "xtra_info" in f_data.keys():
            self.xtra_info = f_data["xtra_info"]
        if self.category == "npcs":
            self.ai.ally = True
            self.indicator_color = "light green"
        if f_data["size"] == "gigantic":
            self.boss = True
            self.occupied_tiles = [(self.x, self.y), (self.x, self.y + 1), (self.x + 1, self.y + 1),
                                   (self.x + 1, self.y)]

        if self.category == "player":
            player_component = Player(50)
            self.player = player_component
            self.player.set_char("player", self.tile)
            self.player.avatar["player"] = self.fighter

    def set_object_components(self):
        self.openable = self.tile["openable"]
        self.pickable = self.tile["pickable"]
        self.interactable = self.tile["interactable"]
        self.light_source = self.tile["light_source"]
        self.blocks = self.tile["blocks"]
