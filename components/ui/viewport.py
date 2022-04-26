from map_objects import tilemap


class Viewport:
    def __init__(self, x, y, w, h):
        self.owner = None
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
        self.dx = 0
        self.dy = 0
        self.offset_x = 0
        self.offset_y = 0
        self.offset_w = 0
        self.offset_h = 0
        self.offset_x2 = 0
        self.offset_y2 = 0
        self.center_x = 0
        self.center_y = 0
        self.offset_center_x = 0
        self.offset_center_y = 0
        self.border = 1
        self.tile_horizontal = tilemap.data.tiles_ui["ui_block_horizontal"]
        self.tile_vertical = tilemap.data.tiles_ui["ui_block_vertical"]
        self.tile_nw = tilemap.data.tiles_ui["ui_block_nw"]
        self.tile_ne = tilemap.data.tiles_ui["ui_block_ne"]
        self.tile_sw = tilemap.data.tiles_ui["ui_block_sw"]
        self.tile_se = tilemap.data.tiles_ui["ui_block_se"]
        self.color = "gray"

    def draw(self):
        self.owner.owner.render_functions.draw_ui(self)

    def update(self, w, h):
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
        self.center_x = int(self.w / 2)
        self.center_y = int(self.h / 2)

    def update_offset(self, offset_x, offset_y):
        self.offset_x = self.x * offset_x
        self.offset_y = self.y * offset_y
        self.offset_w = self.w * offset_x - (offset_x + 1)
        self.offset_h = self.h * offset_y - (offset_y + 1)
        self.offset_x2 = self.offset_x + self.offset_w
        self.offset_y2 = self.offset_y + self.offset_h
        self.offset_center_x = int(self.offset_w / 2)
        self.offset_center_y = int(self.offset_h / 2)
