class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x, y, layer, char, color, name, blocks=False):
        self.x = x
        self.y = y
        self.layer = layer
        self.char = char
        self.char_hub = 0xE100 + 704
        self.color = color
        self.name = name
        self.blocks = blocks
        self.spirit_power = 0

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


def blocking_entity(entities, x, y):
    for entity in entities:
        if entity.blocks and entity.x == x and entity.y == y:
            return entity
    return None
