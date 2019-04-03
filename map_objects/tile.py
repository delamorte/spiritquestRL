class Tile:
    """
    A tile on a map. It may or may not be blocked,
    and may or may not block sight.
    """

    def __init__(self,
                 blocked,
                 block_sight,
                 seed,
                 char=" ",
                 char_ground=0xE100 + 21,
                 layer=0,
                 color=None):
        self.blocked = blocked
        self.block_sight = block_sight
        self.explored = False
        self.seed = seed
        self.char = char
        self.char_ground = char_ground
        self.layer = layer
        self.color = color
        self.spawnable = False
