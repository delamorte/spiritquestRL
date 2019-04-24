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
    Floor tiles are drawn on layer 0, walls and
    other blocked tiles on layer 1 etc.
    """

    def __init__(self,
                 blocked,
                 block_sight,
                 seed=randint(1,100)):
        self.blocked = blocked
        self.block_sight = block_sight
        self.explored = False
        self.seed = seed
        self.char = {0: tilemap()["floor"], 1: " "}
        self.color = {0: "darkest amber", 1: None}
        self.spawnable = False
