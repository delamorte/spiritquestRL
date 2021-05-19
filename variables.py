gfx = "oryx"
tile_height = "48"
tile_width = "32"
tile_offset_x = 0
tile_offset_y = 0
ui_size = "48"
ui_offset_x = 4
ui_offset_y = 3
camera_offset = int(ui_size) / int(tile_height)
camera_width = 0
camera_height = 0
viewport_w = 0
viewport_h = 0
viewport_center_x = 0
viewport_center_y = 0
stack = []
old_stack = []
world_tendency = 0
flicker = False
data = None


class TimeCounter:
    def __init__(self, turn=0):
        self.turn = turn
        self.last_turn = 0
        
    def take_turn(self, action_cost):
        self.last_turn = self.turn
        self.turn += action_cost
        
    def get_turn(self):
        return self.turn

    def get_last_turn(self):
        return self.last_turn
