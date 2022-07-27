from data import json_data
from map_objects import tilemap
from map_objects.tilemap import get_tile_by_attribute
from ui.message import Message


class Door:
    def __init__(self, name=None, status="closed"):
        self.owner = None
        self.name = name
        self.status = status
        if "open" in name:
            self.status = "open"
        elif "locked" in name:
            self.status = "locked"

    def set_status(self, status, game_map):
        self.status = status
        self.name = "door ({0})".format(status)
        self.owner.char = get_tile_by_attribute("name", self.name)

        if status == "open":
            game_map.tiles[self.owner.x][self.owner.y].blocked = False
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False

        else:
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True

    def interaction(self, game_map):
        if self.status == "closed":
            self.set_status("open", game_map)
            msg = "You open the door."
        elif self.status == "open":
            self.set_status("closed", game_map)
            msg = "You close the door."
        else:
            msg = "The door is locked."

        return Message(msg)
