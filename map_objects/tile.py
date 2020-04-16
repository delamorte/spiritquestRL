from map_objects.tilemap import tilemap
from random import randint


class Tile:
    """
    A tile on a map. It may or may not be blocked,
    and may or may not block sight. Each tile has a
    random seed, which may be used to generate
    random events. Tile characters are stored
    in a dictionary, so that each tile can have
    different characters in different layers.
    """

    def __init__(self,
                 blocked,
                 block_sight, x, y):
        self.blocked = blocked
        self.block_sight = block_sight
        self.x = x
        self.y = y
        self.explored = False
        self.visited = False
        self.seed = randint(1, 100)
        self.char = tilemap()["floor"]
        self.layers = []
        self.color = "darkest amber"
        self.name = None
        self.spawnable = False
        self.occupied = False
        self.entities_on_tile = []
        self.natural_light_level = 1
