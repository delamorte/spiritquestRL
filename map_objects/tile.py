class Tile:
    """
    A tile on a map. It may or may not be blocked,
    and may or may not block sight.
    """

    def __init__(self, blocked, block_sight, seed, forest):
        self.blocked = blocked
        self.forest = forest
        self.block_sight = block_sight
        self.seed = seed

        if forest:
            self.blocked = True
            self.block_sight = True
