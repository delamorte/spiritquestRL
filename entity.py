from components.ai import BasicMonster
from components.fighter import Fighter
from map_objects.tilemap import tilemap
from math import sqrt
import tcod
from components import item
from numpy.distutils.from_template import item_re


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, layer, char, color, name, blocks=False, fov=6, player=None, fighter=None, ai=None, item=None, inventory=None):
        self.x = x
        self.y = y
        self.layer = layer
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fov = fov
        self.fighter = fighter
        self.player = player
        self.fighter_c = None
        self.ai = ai
        self.ai_c = None
        self.item = item
        self.inventory = inventory
        self.last_seen_x = x
        self.last_seen_y = y

        if self.player:
            self.spirit_power = 50
            self.char_hub = tilemap()["player"]

        if self.fighter:
            if name is 'player':
                fighter_component = Fighter(
                    hp=20, ac=3, ev=3, power=3, mv_spd=1)
            elif name is 'rat':
                fighter_component = Fighter(
                    hp=10, ac=1, ev=4, power=4, mv_spd=2, atk_spd=1)
                self.fov = 4
            elif name is 'crow':
                fighter_component = Fighter(
                    hp=8, ac=1, ev=6, power=3, mv_spd=1.2, atk_spd=1)
                self.fov = 8
            elif name is 'snake':
                fighter_component = Fighter(
                    hp=12, ac=1, ev=2, power=5, mv_spd=1, atk_spd=1)
            self.fighter_c = fighter_component
            if self.player:
                self.fighter_c.hp += 10
                self.fighter_c.power += 1
            self.fighter_c.max_hp = self.fighter_c.hp
            self.fighter_c.owner = self

        if self.ai:
            if name is 'rat':
                ai_component = BasicMonster()
            elif name is 'crow':
                ai_component = BasicMonster()
            elif name is 'snake':
                ai_component = BasicMonster()
            self.ai_c = ai_component
            self.ai_c.owner = self
            
        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                blocking_entity(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_astar(self, target, entities, game_map):

        fov_map = tcod.map.Map(game_map.width, game_map.height)
        fov_map.walkable[:] = True
        fov_map.transparent[:] = True

        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                if game_map.tiles[x1][y1].blocked:
                    fov_map.walkable[y1, x1] = False
                if game_map.tiles[x1][y1].block_sight:
                    fov_map.transparent[y1, x1] = False

        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                fov_map.walkable[entity.y, entity.x] = False
                fov_map.transparent[entity.y, entity.x] = True
                

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited
        astar = tcod.path.AStar(fov_map)

        # Compute the path between self's coordinates and the target's
        # coordinates
        tcod.path_compute(astar, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters
        # from running around the map if there's an alternative path really far
        # away
        if not tcod.path_is_empty(astar) and tcod.path_size(astar) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(astar, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the
            # corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)


    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return sqrt(dx ** 2 + dy ** 2)


def blocking_entity(entities, x, y):
    for entity in entities:
        if entity.blocks and entity.x == x and entity.y == y:
            return entity
    return None
