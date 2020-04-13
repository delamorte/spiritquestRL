from components.light_source import LightSource

solids = ["solid", "brick", "rock", "stone", "moss", "tree", "dead tree"]
draw_floor_under = ["tree", "dead tree", "fence", "gate", "shrubs"]
light_sources = ["candle", "lantern"]

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
            if self.name not in draw_floor_under:
                game_map.tiles[self.owner.x][self.owner.y].char = " "

        elif self.name == "fence":
            self.block_sight = False
            self.blocked = False
            game_map.tiles[self.owner.x][self.owner.y].blocked = False
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False

        else:
            self.block_sight = False
            self.blocked = True
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False

            if self.name in light_sources:
                light_component = LightSource()
                self.owner.light_source = light_component
                self.owner.light_source.owner = self.owner
                self.owner.light_source.initialize_fov(game_map)
                self.owner.light_source.recompute_fov(self.owner.x, self.owner.y)