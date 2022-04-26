from map_objects import tilemap


class Minimap:
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
        self.tile_horizontal = tilemap.data.tiles_ui["ui_block_horizontal"]
        self.tile_vertical = tilemap.data.tiles_ui["ui_block_vertical"]
        self.tile_nw = tilemap.data.tiles_ui["ui_block_nw"]
        self.tile_ne = tilemap.data.tiles_ui["ui_block_ne"]
        self.tile_sw = tilemap.data.tiles_ui["ui_block_sw"]
        self.tile_se = tilemap.data.tiles_ui["ui_block_se"]
        self.color = "gray"

    def draw(self):
        self.owner.owner.render_functions.draw_ui(self)

    def update(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
