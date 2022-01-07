from math import sqrt
import tcod


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, layer, char, color, name, blocks=False, player=None,
                 fighter=None, ai=None, item=None, inventory=None, stairs=None,
                 wall=None, door=None, cursor=None, light_source=None, abilities=None,
                 status_effects=None, stand_on_messages=True, boss=False):
        self.x = x
        self.y = y
        self.layer = layer
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
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

        for entity in entities["monsters"]:
            if entity.blocks and entity != self and entity != target:
                fov_map.walkable[entity.y, entity.x] = False
                if entity.occupied_tiles is not None:
                    fov_map.walkable[entity.y + 1, entity.x + 1] = False
                    fov_map.walkable[entity.y, entity.x + 1] = False
                    fov_map.walkable[entity.y + 1, entity.x] = False
                fov_map.transparent[entity.y, entity.x] = True

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited
        astar = tcod.path.AStar(fov_map)

        # Compute the path between self's coordinates and the target's
        # coordinates
        tcod.path_compute(astar, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths
        # (for example through other rooms) if for example the player is in a corridor
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
                if self.occupied_tiles is not None:
                    self.occupied_tiles = [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]
        else:
            # Keep the old move function as a backup so that if there are no paths
            # (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the
            # corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

    def distance_to(self, other):
        # Use Chebysev distance
        if self.occupied_tiles is not None:
            return min(max(abs(other.x - self.x), abs(other.y - self.y)),
                       max(abs(other.x - (self.x + 1)), abs(other.y - self.y)),
                       max(abs(other.x - self.x), abs(other.y - (self.y + 1))),
                       max(abs(other.x - (self.x + 1)), abs(other.y - (self.y + 1))))
        else:
            return max(abs(other.x - self.x), abs(other.y - self.y))


def blocking_entity(entities, x, y):
    # TODO: Must be a better way to check this?
    for category in entities.values():
        for entity in category:
            if entity.blocks and entity.occupied_tiles is not None:
                if (x, y) in entity.occupied_tiles:
                    return entity
            elif entity.blocks and entity.x == x and entity.y == y:
                return entity

    return None
