from map_objects.tilemap import tilemap_ui


class MessagePanel:
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
        self.dx = 10
        self.dy = 10
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
        self.draw()
