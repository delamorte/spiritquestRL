from random import randint

from map_gen.tilemap import get_tile, get_color


class Tile:
    """
    A tile on a map. It may or may not be blocked,
    and may or may not block sight. Each tile has a
    random seed, which may be used to generate
    random events. Tile characters are stored
    in a dictionary, so that each tile can have
    different characters in different layers.
    """

    def __init__(self, blocked, block_sight, x=None, y=None):
        self.blocking_entity = None
        self.blocked = blocked
        self.block_sight = block_sight
        self.x = x
        self.y = y
        self.explored = False
        self.visited = False
        self.seed = randint(1, 100)
        self.char = get_tile("floor")
        self.color = get_color("floor")
        self.name = None
        self.spawnable = False
        self.occupied = False
        self.is_door = False
        self.door = None
        self.entities_on_tile = []
        self.items_on_tile = []
        self.stairs = None
        self.natural_light_level = 1.5
        self.targeting_zone = False

    def add_entity(self, entity):
        if entity.door:
            self.is_door = True
            self.door = entity.door

        elif entity.blocks:
            self.blocking_entity = entity
            self.occupied = True

        elif entity.stairs:
            self.stairs = entity.stairs

        elif entity.item:
            self.items_on_tile.append(entity)

        self.entities_on_tile.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities_on_tile:
            self.entities_on_tile.remove(entity)
        if entity in self.items_on_tile:
            self.items_on_tile.remove(entity)
        if entity == self.blocking_entity:
            self.blocking_entity = None
            self.blocked = False
            self.block_sight = False
        if entity.door:
            self.door = None
            self.is_door = False



