class Tile:
    """
    A tile on a map. It may or may not be blocked,
    and may or may not block sight.
    """

    def __init__(self, blocked, block_sight, visited, x, y, seed, forest):
        self.blocked = blocked
        self.block_sight = block_sight
        self.visited = visited
        self.x = x
        self.y = y
        self.seed = seed
        self.forest = forest