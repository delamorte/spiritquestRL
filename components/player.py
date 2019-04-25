from map_objects.tilemap import tilemap

class Player:
    def __init__(self, spirit_power):
        self.spirit_power = spirit_power
        self.char = {"player": tilemap()["player"]}
        self.avatar = {"player": None}
        
        #self.owner.fighter.max_hp += 10
        #self.owner.fighter.hp += 10
        #self.owner.fighter.power += 1