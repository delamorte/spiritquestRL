from components.ai import BasicMonster
from components.fighter import Fighter
from math import sqrt
from tcod import map, path


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, layer, char, color, name, blocks=False, player=None, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.layer = layer
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.player = player
        self.fighter_c = None
        self.ai = ai
        self.ai_c = None

        if self.player:
            self.spirit_power = 30
            self.char_hub = 0xE100 + 704

        if self.fighter:
            if name is 'Player':
                fighter_component = Fighter(hp=20, ac=3, ev=3, power=3)
            elif name is 'Cat':
                fighter_component = Fighter(hp=10, ac=1, ev=5, power=2)
            elif name is 'Crow':
                fighter_component = Fighter(hp=8, ac=1, ev=5, power=5)
            elif name is 'Snake':
                fighter_component = Fighter(hp=10, ac=3, ev=3, power=3)
            self.fighter_c = fighter_component
            self.fighter_c.max_hp = self.fighter_c.hp
            self.fighter_c.owner = self

        if self.ai:
            if name is 'Cat':
                ai_component = BasicMonster()
            elif name is 'Crow':
                ai_component = BasicMonster()
            elif name is 'Snake':
                ai_component = BasicMonster()
            self.ai_c = ai_component
            self.ai_c.owner = self

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

        fov_map = map.Map(game_map.width, game_map.height)
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

        astar = path.AStar(fov_map)
        fov_map.compute_fov(self.x, self.y, 10)
        path_xy = astar.get_path(self.x, self.y, target.x, target.y)
        if len(path_xy) > 0:
            self.x, self.y = path_xy[0]
        else:
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
