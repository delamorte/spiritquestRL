class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, layer, char, color):
        self.x = x
        self.y = y
        self.layer = layer
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
