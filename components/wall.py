from map_objects.tilemap import get_tile_object


class Wall:
    def __init__(self, name=None, tile=None, status=None, blocked=True, block_sight=True):
        self.owner = None
        self.name = name
        if not tile:
            tile = get_tile_object(name)
        self.tile = tile
        self.status = status
        self.blocked = blocked
        self.block_sight = block_sight

    def set_attributes(self, game_map):

        if self.tile["blocks_sight"]:
            self.block_sight = True
            self.blocked = True
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True
            if not self.tile["draw_floor"]:
                game_map.tiles[self.owner.x][self.owner.y].char = " "

        else:
            self.block_sight = False
            self.blocked = True
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False
