from ctypes import c_uint32, addressof
from bearlibterminal import terminal as blt
import pickle

data = None


class Tilemap:
    def __init__(self, tileset="oryx"):
        self.tileset = tileset
        self.tiles = None
        self.tiles_ui = None
        self.openables_names = ["gate",
                     "gate (open)",
                     "gate (closed)",
                     "gate (locked)",
                     "door",
                     "door (open)",
                     "door (closed)",
                     "door (locked)"]
        self.items_names = ["flask", "skull", "book", "bone", "candle"]
        self.stairs_names = ["campfire", "holy symbol"]

    def init_gfx(self, f):
        with open(f, 'rb') as gfx:
            tileset = pickle.load(gfx)

        arr = (c_uint32 * len(tileset))(*tileset)
        return arr

    def init_tiles(self, options):
        tilesize = options.tile_width + 'x' + options.tile_height

        gfx1 = self.init_gfx('./gfx/gfx1')
        gfx2 = self.init_gfx('./gfx/gfx2')
        gfx3 = self.init_gfx('./gfx/gfx3')
        gfx4 = self.init_gfx('./gfx/gfx4')
        gfx5 = self.init_gfx('./gfx/gfx5')
        gfx6 = self.init_gfx('./gfx/gfx6')

        blt.set("U+E000: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
                tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

        blt.set("U+E400: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx2), 320, 1080) +
                tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

        blt.set("U+E800: %d, \
             size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx3), 288, 168) +
                tilesize + ", resize-filter=nearest, spacing=4x4 align=top-left")

        blt.set("U+F000: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx4), 176, 240) +
                "32x48" + ", resize-filter=nearest, spacing=4x4, align=top-left")

        blt.set("U+F100: %d, \
            size=32x32, raw-size=%dx%d, resize=" % (addressof(gfx5), 192, 448) +
                "32x32" + ", resize-filter=nearest, spacing=4x4, align=top-left")

        # Big tiles
        blt.set("U+F300: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx6), 144, 48) +
                "64x96" + ", resize-filter=nearest, spacing=4x4, align=top-left")

        options.tile_offset_x = int(
            int(options.tile_width) / blt.state(blt.TK_CELL_WIDTH))
        options.tile_offset_y = int(
            int(options.tile_height) / blt.state(blt.TK_CELL_HEIGHT))

        self.tiles = self.map_tiles()
        self.tiles_ui = self.map_tiles_ui()

        blt.clear()

    def map_tiles_ui(self):

        tiles_ui = {
            "ui_block_horizontal": 0xF000 + 26,
            "ui_block_vertical": 0xF000 + 27,
            "ui_block_nw": 0xF000 + 22,
            "ui_block_ne": 0xF000 + 23,
            "ui_block_sw": 0xF000 + 24,
            "ui_block_se": 0xF000 + 25,
        }
        return tiles_ui

    def map_tiles(self, tileset=None):

        if tileset is None:
            tileset = self.tileset

        if tileset == "oryx":
            tiles = {"tree": (0xE000 + 399, 0xE000 + 400, 0xE000 + 401, 0xE000 + 402, 0xE000 + 405),
                     "dead_tree": (0xE000 + 403, 0xE000 + 404),
                     "coffin": {"open": 0xE000 + 50, "closed": 0xE800 + 151},
                     "shrine": (0xE000 + 55, 0xE000 + 56, 0xE000 + 57, 0xE000 + 58),
                     "candle": 0xE400 + 520,
                     "candelabra": 0xE400 + 70,
                     "gate": {"open": 0xE000 + 103, "closed": 0xE800 + 102, "locked": 0xE800 + 102},
                     "fence": (0xE000 + 107, 0xE000 + 101),
                     "statue": (0xE000 + 61, 0xE000 + 62, 0xE000 + 63, 0xE000 + 64),
                     "ground_soil": (0xE000 + 692,),
                     "ground_moss": (0xE000 + 186,),
                     "ground_dot": (0xE000 + 293),
                     "floor": 0xE000 + 237,
                     "floor_wood": 0xE000 + 264,
                     "plants": (
                         0xE400 + 120, 0xE400 + 121, 0xE400 + 122, 0xE400 + 123, 0xE400 + 200, 0xE400 + 201, 0xE400 + 202),
                     "flowers": (0xE400 + 127, 0xE400 + 128, 0xE400 + 129),
                     "mushrooms": (0xE400 + 131),
                     "rocks": (0xE400 + 132, 0xE400 + 133),
                     "bones": (0xE000 + 362, 0xE000 + 363, 0xE000 + 364, 0xE000 + 365, 0xE000 + 366),
                     "player": 0xE000 + 460,
                     "player_remains": 0xE000 + 379,
                     "monsters": {"rat": 0xE000 + 495,
                                  "bear": 0xE000 + 526,
                                  "crow": 0xE000 + 509,
                                  "felid": 0xE000 + 505,
                                  "snake": 0xE000 + 502,
                                  "frog": 0xE000 + 504,
                                  "mosquito": 0xE000 + 524},
                     "monsters_chaos": {"rat": 0xE000 + 498,
                                        "crow": 0xE000 + 509,
                                        "chaos cat": 0xE000 + 506,
                                        "chaos bear": 0xE000 + 529,
                                        "chaos spirit": 0xE000 + 638,
                                        "cockroach": 0xE000 + 517,
                                        "bone snake": 0xE000 + 511,
                                        "chaos dog": 0xE000 + 499,
                                        "bat": 0xE000 + 500,
                                        "imp": 0xE000 + 555,
                                        "leech": 0xE000 + 614},
                     "monsters_light": {"bear": 0xE000 + 528,
                                        "crow": 0xE000 + 509,
                                        "spirit": 0xE000 + 636,
                                        "ghost dog": 0xE000 + 605,
                                        "snake": 0xE000 + 502,
                                        "gecko": 0xE000 + 503,
                                        "serpent": 0xE000 + 512,
                                        "frog": 0xE000 + 504,
                                        "mosquito": 0xE000 + 524,
                                        "fairy": 0xE000 + 579},

                     "unique_monsters": {"king kobra": 0xF300 + 1, "albino rat": 0xE000 + 498,
                                         "keeper of dreams": 0xF300 + 0},
                     "monster_remains": 0xE400 + 86,
                     "boss_remains": 0xF300 + 9,
                     "door": {"open": 0xE000 + 307, "closed": 0xE000 + 306, "locked": 0xE000 + 308},
                     "campfire": 0xE000 + 303,
                     "stairs": {"up": 0xE000 + 324, "down": 0xE000 + 323},
                     # Walls
                     "brick": {"horizontal": 0xE000 + 247, "vertical": 0xE000 + 235},
                     "brick wall, horizontal": 0xE000 + 247,
                     "brick wall, vertical": 0xE000 + 235,
                     "moss": (0xE000 + 256, 0xE000 + 236),
                     "weapons": {"club": 0xE000 + 67},
                     "ui_block_horizontal": 0xE000 + 688,
                     "ui_block_vertical": 0xE000 + 689,
                     "ui_block_nw": 0xE000 + 684,
                     "ui_block_ne": 0xE000 + 685,
                     "ui_block_sw": 0xE000 + 686,
                     "ui_block_se": 0xE000 + 687,
                     "indicator": 0xE000 + 672,
                     "cursor": 0xF000 + 9
                     }

        else:
            tiles = {"tree": ("T", "t"),
                     "dead_tree": ("T", "t"),
                     "rocks": "^",
                     "coffin": "¤",
                     "coffin (open)": "¤",
                     "coffin (closed)": "¤",
                     "shrine": "£",
                     "mushrooms": ",",
                     "candle": "~",
                     "gate": {"open": "-", "closed": "+", "locked": "*"},
                     "gate (open)": "-",
                     "gate (closed)": "+",
                     "fence": "|",
                     "fence, horizontal": "|",
                     "fence, vertical": "|",
                     "statue": "&",
                     "ground_soil": ".",
                     "ground_moss": ".",
                     "ground_dot": ".",
                     "floor": ".",
                     "flowers": "*",
                     "floor_wood": ".",
                     "pavement": ".",
                     "rubble": ".",
                     "shrubs": "`",
                     "bones": ",",
                     "player": "@",
                     "player_remains": "@",
                     "monsters": {"rat": "r",
                                  "bear": "B",
                                  "crow": "c",
                                  "felid": "f",
                                  "snake": "s",
                                  "frog": "f",
                                  "mosquito": "m"},
                     "monsters_chaos": {"rat": "R",
                                        "crow": "C",
                                        "chaos cat": "C",
                                        "chaos bear": "B",
                                        "chaos spirit": "S",
                                        "cockroach": "r",
                                        "bone snake": "S",
                                        "chaos dog": "D",
                                        "bat": "b",
                                        "imp": "I",
                                        "leech": "l"},
                     "monsters_light": {"bear": "B",
                                        "crow": "c",
                                        "spirit": "S",
                                        "ghost dog": "D",
                                        "snake": "s",
                                        "gecko": "g",
                                        "serpent": "§",
                                        "frog": "f",
                                        "mosquito": "m",
                                        "fairy": "F"},

                     "unique_monsters": {"king kobra": "K", "albino rat": "R", "keeper of dreams": "K"},
                     "monster_remains": "%",
                     "boss_remains": "%",
                     "door": {"open": "-", "closed": "+", "locked": "+"},
                     "door (closed)": "+",
                     "door (open)": "-",
                     "campfire": "æ",
                     "stairs": {"up": "<", "down": ">"},
                     "brick": {"horizontal": "#", "vertical": "#"},
                     "wall": "#",
                     "window": "~",
                     "holy symbol": "+",
                     "cross": "+",
                     "skull": ",",
                     "book": "?",
                     "flask": "!",
                     "table": "t",
                     "throne": "T",
                     "moss": "#",
                     "weapons": {"club": "\\"},
                     "ui_block_horizontal": 0xE800 + 472,
                     "ui_block_vertical": 0xE800 + 440,
                     "ui_block_nw": 0xE800 + 468,
                     "ui_block_ne": 0xE800 + 468,
                     "ui_block_sw": 0xE800 + 468,
                     "ui_block_se": 0xE800 + 468,
                     "indicator": 0xE800 + 1746
                     }

        return tiles
