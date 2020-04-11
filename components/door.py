from map_objects.tilemap import tilemap


class Door:
    def __init__(self, name=None, status="closed"):
        self.owner = None
        self.name = name
        self.status = status
        
    def set_status(self, status, game_map):
        if status == "open":
            self.status = "open"
            game_map.tiles[self.owner.x][self.owner.y].blocked = False
            game_map.tiles[self.owner.x][self.owner.y].block_sight = False
            self.owner.char = tilemap()["door"]["open"]
        if status == "closed":
            self.status = "closed"
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True       
            self.owner.char = tilemap()["door"]["closed"]     
        if status == "locked":
            self.status = "locked"
            game_map.tiles[self.owner.x][self.owner.y].blocked = True
            game_map.tiles[self.owner.x][self.owner.y].block_sight = True    
            self.owner.char = tilemap()["door"]["locked"]
