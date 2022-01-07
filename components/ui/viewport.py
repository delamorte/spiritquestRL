from map_objects.tilemap import tilemap_ui


class Viewport:
    def __init__(self, x, y, w, h):
        self.owner = None
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.content_x = x+1
        self.content_y = y+1
        self.content_w = w-1
        self.content_h = h-1
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
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

    def update(self, w, h):
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
        self.content_x = self.x+1
        self.content_y = self.y+1
        self.content_w = self.w-1
        self.content_h = self.h-1
        self.center_x = int(self.w / 2)
        self.center_y = int(self.h / 2)
