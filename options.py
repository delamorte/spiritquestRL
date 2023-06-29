data = None


class Options:
    def __init__(self, gfx="oryx", tile_height="48", tile_width="32", ui_size="48",
                 flicker=False, debug=False):
        self.gfx = gfx
        self.tile_height = tile_height
        self.tile_width = tile_width
        self.tile_offset_x = 0
        self.tile_offset_y = 0
        self.ui_size = ui_size
        self.flicker = flicker
        self.indicator = 0xE000 + 672
        self.initial_animals = ("crow", "rat", "snake")
        self.debug = debug
