

solids = ["solid", "brick", "rock", "stone", "moss", "tree", "dead tree"]

class Wall:
    def __init__(self, name=None, status=None, blocked=True, block_sight=True):
        self.owner = None
        self.name = name
        self.status = status
        self.blocked = blocked
        self.block_sight = block_sight

    def set_attributes(self, game_map):

        if self.name in solids:
            self.block_sight = True
            self.blocked = True
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True

        else:
            self.block_sight = False
            self.blocked = True
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False
