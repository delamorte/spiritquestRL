from map_objects.tilemap import tilemap_ui


class MessagePanel:
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
        self.border = 1
        self.border_offset = 0
        self.tile_horizontal = tilemap_ui()["ui_block_horizontal"]
        self.tile_vertical = tilemap_ui()["ui_block_vertical"]
        self.tile_nw = tilemap_ui()["ui_block_nw"]
        self.tile_ne = tilemap_ui()["ui_block_ne"]
        self.tile_sw = tilemap_ui()["ui_block_sw"]
        self.tile_se = tilemap_ui()["ui_block_se"]
        self.color = "gray"

    def draw(self):
        self.owner.render_functions.draw_ui(self)

    def update(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h

    def update_offset(self, offset_x, offset_y):
        self.offset_x = self.x * offset_x
        self.offset_y = self.y * offset_y
        self.offset_w = self.w * offset_x - (offset_x + 1)
        self.offset_h = self.h * offset_y - (offset_y + 1)
        self.offset_x2 = self.offset_x + self.offset_w
        self.offset_y2 = self.offset_y + self.offset_h
        self.border_offset = self.border * offset_x + 1