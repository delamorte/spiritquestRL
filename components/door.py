from map_objects import tilemap
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
        if status == "open":
            self.status = "open"
            game_map.tiles[self.owner.x][self.owner.y].blocked = False
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False
            self.owner.char = tilemap.data.tiles["door"]["open"]
            self.name = "door (open)"
        if status == "closed":
            self.status = "closed"
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True       
            self.owner.char = tilemap.data.tiles["door"]["closed"]
            self.name = "door (closed)"
        if status == "locked":
            self.status = "locked"
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True    
            self.owner.char = tilemap.data.tiles["door"]["locked"]

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
