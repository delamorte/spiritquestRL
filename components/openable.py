from map_objects.tilemap import get_tile_object, get_tile
from ui.message import Message


class Openable:
    def __init__(self, name=None, char=None, state="closed"):
        self.owner = None
        self.name = name
        self.char = char
        self.state = state
        self.tile = get_tile_object(name)
        if char == self.tile["locked"]:
            self.state = "locked"
        elif char == self.tile["closed"]:
            self.state = "closed"

    def set_state(self, state, game_map):
        self.state = state
        self.owner.char = get_tile(self.name, self.tile, state)

        if state == "open":
            game_map.tiles[self.owner.x][self.owner.y].blocked = False
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False

        else:
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True

    def interaction(self, game_map):
        if self.state == "locked":
            msg = "The {0} is locked.".format(self.name)
        elif self.state == "closed":
            self.set_state("open", game_map)
            msg = "You open the {0}.".format(self.name)
        else:
            self.set_state("closed", game_map)
            msg = "You close the {0}.".format(self.name)

        return Message(msg)
