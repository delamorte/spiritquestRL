gfx = "tiles"
tilesize = "32"
ui_size = "32"
tile_offset_x = 0
tile_offset_y = 0
ui_offset_x = 0
ui_offset_y = 0
camera_offset = int(ui_size) / int(tilesize)

class TimeCounter:
    def __init__(self, turn=0):
        self.turn = turn
        self.last_turn = 0
        
    def take_turn(self, action_cost):
        self.last_turn = self.turn
        self.turn += action_cost
        print("current turn: " + str(self.turn))
        print("last turn: " + str(self.last_turn))
        
    def get_turn(self):
        return self.turn
    def get_last_turn(self):
        return self.last_turn