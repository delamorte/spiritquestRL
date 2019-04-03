class Tile:
    """
    A tile on a map. It may or may not be blocked,
    and may or may not block sight.
    """

    def __init__(self, blocked, block_sight, x, y, seed, forest, char=" ", char_ground=" ", layer=0, color=None):
        self.blocked = blocked
        self.block_sight = block_sight
        self.explored = False
        self.x = x
        self.y = y
        self.seed = seed
        self.forest = forest
        self.char = char
        self.char_ground = char_ground
        self.layer = layer
        self.color = color
