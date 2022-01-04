from ctypes import c_uint32, addressof
from bearlibterminal import terminal as blt
from palettes import name_color_from_value
import settings
from os import path
import pickle

openables = ["gate",
             "gate (open)",
             "gate (closed)",
             "gate (locked)",
             "door",
             "door (open)",
             "door (closed)",
             "door (locked)"]

items = ["flask", "skull", "book", "bone", "candle"]

stairs = ["campfire", "holy symbol"]

def init_gfx(f):
    with open(f, 'rb') as gfx:
        tileset = pickle.load(gfx)

    arr = (c_uint32 * len(tileset))(*tileset)
    return arr


def init_tiles():
    tilesize = settings.tile_width + 'x' + settings.tile_height

    gfx1 = init_gfx('./gfx/gfx1')
    gfx2 = init_gfx('./gfx/gfx2')
    gfx3 = init_gfx('./gfx/gfx3')
    gfx4 = init_gfx('./gfx/gfx4')
    gfx5 = init_gfx('./gfx/gfx5')
    gfx6 = init_gfx('./gfx/gfx6')

    blt.set("U+E000: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
            tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

    blt.set("U+E400: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx2), 320, 1080) +
            tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

    blt.set("U+E800: %d, \
        size=16x16, raw-size=%dx%d, resize=" % (addressof(gfx3), 512, 960) +
            tilesize + ", resize-filter=nearest, align=top-left")

    # Interface
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

    settings.tile_offset_x = int(
        int(settings.tile_width) / blt.state(blt.TK_CELL_WIDTH))
    settings.tile_offset_y = int(
        int(settings.tile_height) / blt.state(blt.TK_CELL_HEIGHT))

    blt.clear()


def tilemap_ui():
    tiles = {
        "ui_block_horizontal": 0xF000 + 26,
        "ui_block_vertical": 0xF000 + 27,
        "ui_block_nw": 0xF000 + 22,
        "ui_block_ne": 0xF000 + 23,
        "ui_block_sw": 0xF000 + 24,
        "ui_block_se": 0xF000 + 25,
    }
    return tiles


def tilemap(tileset=None):
    tiles = {}
    if tileset is None:
        tileset = settings.gfx
    if tileset == "adambolt":
        tiles = {"tree": (0xE800 + 87, 0xE800 + 88, 0xE800 + 89, 0xE800 + 93, 0xE800 + 94, 0xE800 + 95),
                 "dead_tree": (0xE800 + 112, 0xE800 + 144),
                 "rocks": (0xE800 + 388, 0xE800 + 119),
                 "coffin (open)": 0xE800 + 158,
                 "coffin (closed)": 0xE800 + 158,
                 "shrine": 0xE800 + 107,
                 "candle": 0xE800 + 458,
                 "gate": {"open": 0xE800 + 68, "closed": 0xE800 + 67, "locked": 0xE800 + 78},
                 "gate (open)": 0xE800 + 68,
                 "gate (closed)": 0xE800 + 67,
                 "fence, vertical": 0xE800 + 440,
                 "fence, horizontal": 0xE800 + 441,
                 "statue": 0xE800 + 945,
                 "shrubs": 0xE800 + 93,
                 "plants": (0xE800 + 93, 0xE800 + 94, 0xE800 + 95),
                 "flowers": (0xE800 + 93, 0xE800 + 94, 0xE800 + 95),
                 "mushrooms": (0xE800 + 118),
                 "ground_dot": (0xE800 + 1748),
                 "ground_soil": (0xE800 + 1748, 0xE800 + 1750),
                 "ground_moss": (0xE800 + 1751, 0xE800 + 1752, 0xE800 + 1753),
                 "floor": 0xE800 + 20,
                 "floor_wood": 0xE800 + 21,
                 "pavement": (0xE800 + 20),
                 "bones": (0xE800 + 468, 0xE800 + 469, 0xE800 + 470, 0xE800 + 471, 0xE800 + 475),
                 "player": 0xE800 + 704,
                 "player_remains": 0xE800 + 468,
                 "monsters": {"rat": 0xE800 + 1416,
                              "bear": 0xE800 + 1780,
                              "crow": 0xE800 + 1587,
                              "felid": 0xE800 + 1252,
                              "snake": 0xE800 + 1097,
                              "frog": 0xE800 + 1095,
                              "mosquito": 0xE800 + 1554},
                 "monsters_chaos": {"rat": 0xE800 + 1416,
                                    "crow": 0xE800 + 1587,
                                    "chaos cat": 0xE800 + 1255,
                                    "chaos bear": 0xE800 + 1553,
                                    "chaos spirit": 0xE800 + 1029,
                                    "cockroach": 0xE800 + 1473,
                                    "bone snake": 0xE800 + 1093,
                                    "chaos dog": 0xE800 + 960,
                                    "bat": 0xE800 + 1200,
                                    "imp": 0xE800 + 1047,
                                    "leech": 0xE800 + 1204},
                 "monsters_light": {"bear": 0xE800 + 1780,
                                    "crow": 0xE800 + 1587,
                                    "spirit": 0xE800 + 1017,
                                    "ghost dog": 0xE800 + 959,
                                    "snake": 0xE800 + 1100,
                                    "gecko": 0xE800 + 1104,
                                    "serpent": 0xE800 + 1323,
                                    "frog": 0xE800 + 1095,
                                    "mosquito": 0xE800 + 1554,
                                    "fairy": 0xE800 + 1032},

                 "unique_monsters": {"king kobra": 0xE800 + 1105, "albino rat": 0xE800 + 1414,
                                     "keeper of dreams": 0xE800 + 974},
                 "monster_remains": 0xE800 + 513,
                 "boss_remains": 0xE800 + 513,
                 "door": {"open": 0xE800 + 68, "closed": 0xE800 + 67, "locked": 0xE800 + 78},
                 "door (open)": 0xE800 + 68,
                 "door (closed)": 0xE800 + 67,
                 "campfire": 0xE800 + 427,
                 "holy symbol": 0xE800 + 439,
                 "cross": 0xE800 + 438,
                 "stairs": {"up": 0xE800 + 22, "down": 0xE800 + 27},
                 "brick": {"horizontal": 0xE800 + 83, "vertical": 0xE800 + 83},
                 "wall": 0xE800 + 83,
                 "window": 0xE800 + 82,
                 "throne": 0xE800 + 107,
                 "table": 0xE800 + 107,
                 "book": 0xE800 + 409,
                 "skull": 0xE800 + 468,
                 "flask": 0xE800 + 160,
                 "moss": (0xE800 + 90, 0xE800 + 91, 0xE800 + 92),
                 "weapons": {"club": 0xE800 + 242},
                 "ui_block_horizontal": 0xE800 + 472,
                 "ui_block_vertical": 0xE800 + 440,
                 "ui_block_nw": 0xE800 + 468,
                 "ui_block_ne": 0xE800 + 468,
                 "ui_block_sw": 0xE800 + 468,
                 "ui_block_se": 0xE800 + 468,
                 "indicator": 0xE800 + 1746
                 }

    elif tileset == "oryx":
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
                 "indicator": 0xE000 + 671,
                 "indicator_2x2": 0xF300 + 10
                 }

    elif tileset == "ascii":
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
