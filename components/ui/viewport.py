from map_objects.tilemap import tilemap_ui


class Viewport:
    def __init__(self, x, y, w, h):
        self.owner = None
        self.borders_x = x
        self.borders_y = y
        self.borders_w = w
        self.borders_h = h
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
        self.borders_x2 = self.borders_x + self.borders_w
        self.borders_y2 = self.borders_y + self.borders_h
        self.dx = 0
        self.dy = 0
        self.center_x = 0
        self.center_y = 0
        self.tile_horizontal = tilemap_ui()["ui_block_horizontal"]
        self.tile_vertical = tilemap_ui()["ui_block_vertical"]
        self.tile_nw = tilemap_ui()["ui_block_nw"]
        self.tile_ne = tilemap_ui()["ui_block_ne"]
        self.tile_sw = tilemap_ui()["ui_block_sw"]
        self.tile_se = tilemap_ui()["ui_block_se"]
        self.color = "gray"

    def draw(self):
        self.owner.render_functions.draw_ui(self)

    def update_borders(self, w, h, x=0, y=0):
        self.borders_x = x
        self.borders_y = y
        self.borders_w = w
        self.borders_h = h
        self.borders_x2 = self.borders_x + self.borders_w
        self.borders_y2 = self.borders_y + self.borders_h

    def update(self, w, h):
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
        self.center_x = int(self.w / 2)
        self.center_x = int(self.h / 2)
