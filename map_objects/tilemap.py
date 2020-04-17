from ctypes import c_uint32, addressof
from bearlibterminal import terminal as blt
from palettes import name_color_from_value
import variables
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
    tilesize = variables.tile_width + 'x' + variables.tile_height

    gfx1 = init_gfx('./gfx/gfx1')
    gfx2 = init_gfx('./gfx/gfx2')
    gfx3 = init_gfx('./gfx/gfx3')

    blt.set("U+E100: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
            tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

    blt.set("U+E500: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx2), 320, 1080) +
            tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

    blt.set("U+E900: %d, \
        size=16x16, raw-size=%dx%d, resize=" % (addressof(gfx3), 512, 960) +
            tilesize + ", resize-filter=nearest, align=top-left")

    blt.set("U+F100: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
            "32x48" + ", resize-filter=nearest, spacing=4x4, align=top-left")

    blt.set("U+F500: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
            "64x96" + ", resize-filter=nearest, spacing=4x4, align=top-left")

    variables.tile_offset_x = int(
        int(variables.tile_width) / blt.state(blt.TK_CELL_WIDTH))
    variables.tile_offset_y = int(
        int(variables.tile_height) / blt.state(blt.TK_CELL_HEIGHT))
    variables.camera_offset = int(variables.ui_size) / int(variables.tile_height)

    blt.clear()


def tilemap_ui():
    tiles = {
        "ui_block_horizontal": 0xF100 + 707,
        "ui_block_vertical": 0xF100 + 708,
        "ui_block_nw": 0xF100 + 703,
        "ui_block_ne": 0xF100 + 704,
        "ui_block_sw": 0xF100 + 705,
        "ui_block_se": 0xF100 + 706,
    }
    return tiles


def tilemap(tileset=None):
    tiles = {}
    if tileset is None:
        tileset = variables.gfx
    if tileset == "adambolt":
        tiles = {"tree": (0xE900 + 87, 0xE900 + 88, 0xE900 + 89, 0xE900 + 93, 0xE900 + 94, 0xE900 + 95),
                 "dead_tree": (0xE900 + 112, 0xE900 + 144),
                 "rocks": (0xE900 + 388, 0xE900 + 119),
                 "coffin (open)": 0xE900 + 158,
                 "coffin (closed)": 0xE900 + 158,
                 "shrine": 0xE900 + 107,
                 "candle": 0xE900 + 458,
                 "gate": {"open": 0xE900 + 68, "closed": 0xE900 + 67, "locked": 0xE900 + 78},
                 "gate (open)": 0xE900 + 68,
                 "gate (closed)": 0xE900 + 67,
                 "fence, vertical": 0xE900 + 440,
                 "fence, horizontal": 0xE900 + 441,
                 "statue": 0xE900 + 945,
                 "shrubs": 0xE900 + 93,
                 "plants": (0xE900 + 93, 0xE900 + 94, 0xE900 + 95),
                 "flowers": (0xE900 + 93, 0xE900 + 94, 0xE900 + 95),
                 "mushrooms": (0xE900 + 118),
                 "ground_dot": (0xE900 + 1748),
                 "ground_soil": (0xE900 + 1748, 0xE900 + 1750),
                 "ground_moss": (0xE900 + 1751, 0xE900 + 1752, 0xE900 + 1753),
                 "floor": 0xE900 + 20,
                 "floor_wood": 0xE900 + 21,
                 "pavement": (0xE900 + 20),
                 "bones": (0xE900 + 468, 0xE900 + 469, 0xE900 + 470, 0xE900 + 471, 0xE900 + 475),
                 "player": 0xE900 + 704,
                 "player_remains": 0xE900 + 468,
                 "monsters": {"rat": 0xE900 + 1416,
                              "bear": 0xE900 + 1780,
                              "crow": 0xE900 + 1587,
                              "felid": 0xE900 + 1252,
                              "snake": 0xE900 + 1097,
                              "frog": 0xE900 + 1095,
                              "mosquito": 0xE900 + 1554},
                 "monsters_chaos": {"rat": 0xE900 + 1416,
                                    "crow": 0xE900 + 1587,
                                    "chaos cat": 0xE900 + 1255,
                                    "chaos bear": 0xE900 + 1553,
                                    "chaos spirit": 0xE900 + 1029,
                                    "cockroach": 0xE900 + 1473,
                                    "bone snake": 0xE900 + 1093,
                                    "chaos dog": 0xE900 + 960,
                                    "bat": 0xE900 + 1200,
                                    "imp": 0xE900 + 1047,
                                    "leech": 0xE900 + 1204},
                 "monsters_light": {"bear": 0xE900 + 1780,
                                    "crow": 0xE900 + 1587,
                                    "spirit": 0xE900 + 1017,
                                    "ghost dog": 0xE900 + 959,
                                    "snake": 0xE900 + 1100,
                                    "gecko": 0xE900 + 1104,
                                    "serpent": 0xE900 + 1323,
                                    "frog": 0xE900 + 1095,
                                    "mosquito": 0xE900 + 1554,
                                    "fairy": 0xE900 + 1032},

                 "unique_monsters": {"king kobra": 0xE900 + 1105, "albino rat": 0xE900 + 1414,
                                     "keeper of dreams": 0xE900 + 974},
                 "monster_remains": 0xE900 + 513,
                 "boss_remains": 0xE900 + 513,
                 "door": {"open": 0xE900 + 68, "closed": 0xE900 + 67, "locked": 0xE900 + 78},
                 "door (open)": 0xE900 + 68,
                 "door (closed)": 0xE900 + 67,
                 "campfire": 0xE900 + 427,
                 "holy symbol": 0xE900 + 439,
                 "cross": 0xE900 + 438,
                 "stairs": {"up": 0xE900 + 22, "down": 0xE900 + 27},
                 "brick": {"horizontal": 0xE900 + 83, "vertical": 0xE900 + 83},
                 "wall": 0xE900 + 83,
                 "window": 0xE900 + 82,
                 "throne": 0xE900 + 107,
                 "table": 0xE900 + 107,
                 "book": 0xE900 + 409,
                 "skull": 0xE900 + 468,
                 "flask": 0xE900 + 160,
                 "moss": (0xE900 + 90, 0xE900 + 91, 0xE900 + 92),
                 "weapons": {"club": 0xE900 + 242},
                 "ui_block_horizontal": 0xE900 + 472,
                 "ui_block_vertical": 0xE900 + 440,
                 "ui_block_nw": 0xE900 + 468,
                 "ui_block_ne": 0xE900 + 468,
                 "ui_block_sw": 0xE900 + 468,
                 "ui_block_se": 0xE900 + 468,
                 "indicator": 0xE900 + 1746
                 }

    elif tileset == "oryx":
        tiles = {"tree": (0xE100 + 399, 0xE100 + 400, 0xE100 + 401, 0xE100 + 402, 0xE100 + 405),
                 "dead_tree": (0xE100 + 403, 0xE100 + 404),
                 "coffin": {"open": 0xE100 + 50, "closed": 0xE900 + 151},
                 "shrine": (0xE100 + 55, 0xE100 + 56, 0xE100 + 57, 0xE100 + 58),
                 "candle": 0xE500 + 520,
                 "candelabra": 0xE500 + 70,
                 "gate": {"open": 0xE100 + 103, "closed": 0xE900 + 102, "locked": 0xE900 + 102},
                 "fence": (0xE100 + 107, 0xE100 + 101),
                 "statue": (0xE100 + 61, 0xE100 + 62, 0xE100 + 63, 0xE100 + 64),
                 "ground_soil": (0xE100 + 692,),
                 "ground_moss": (0xE100 + 186,),
                 "ground_dot": (0xE100 + 293),
                 "floor": 0xE100 + 237,
                 "floor_wood": 0xE100 + 264,
                 "plants": (
                     0xE500 + 120, 0xE500 + 121, 0xE500 + 122, 0xE500 + 123, 0xE500 + 200, 0xE500 + 201, 0xE500 + 202),
                 "flowers": (0xE500 + 127, 0xE500 + 128, 0xE500 + 129),
                 "mushrooms": (0xE500 + 131),
                 "rocks": (0xE500 + 132, 0xE500 + 133),
                 "bones": (0xE100 + 362, 0xE100 + 363, 0xE100 + 364, 0xE100 + 365, 0xE100 + 366),
                 "player": 0xE100 + 460,
                 "player_remains": 0xE100 + 379,
                 "monsters": {"rat": 0xE100 + 495,
                              "bear": 0xE100 + 526,
                              "crow": 0xE100 + 509,
                              "felid": 0xE100 + 505,
                              "snake": 0xE100 + 502,
                              "frog": 0xE100 + 504,
                              "mosquito": 0xE100 + 524},
                 "monsters_chaos": {"rat": 0xE100 + 498,
                                    "crow": 0xE100 + 509,
                                    "chaos cat": 0xE100 + 506,
                                    "chaos bear": 0xE100 + 529,
                                    "chaos spirit": 0xE100 + 638,
                                    "cockroach": 0xE100 + 517,
                                    "bone snake": 0xE100 + 511,
                                    "chaos dog": 0xE100 + 499,
                                    "bat": 0xE100 + 500,
                                    "imp": 0xE100 + 555,
                                    "leech": 0xE100 + 614},
                 "monsters_light": {"bear": 0xE100 + 528,
                                    "crow": 0xE100 + 509,
                                    "spirit": 0xE100 + 636,
                                    "ghost dog": 0xE100 + 605,
                                    "snake": 0xE100 + 502,
                                    "gecko": 0xE100 + 503,
                                    "serpent": 0xE100 + 512,
                                    "frog": 0xE100 + 504,
                                    "mosquito": 0xE100 + 524,
                                    "fairy": 0xE100 + 579},

                 "unique_monsters": {"king kobra": 0xE100 + 602, "albino rat": 0xE100 + 498,
                                     "keeper of dreams": 0xF500 + 645},
                 "monster_remains": 0xE500 + 86,
                 "boss_remains": 0xF500 + 366,
                 "door": {"open": 0xE100 + 307, "closed": 0xE100 + 306, "locked": 0xE100 + 308},
                 "campfire": 0xE100 + 303,
                 "stairs": {"up": 0xE100 + 324, "down": 0xE100 + 323},
                 # Walls
                 "brick": {"horizontal": 0xE100 + 247, "vertical": 0xE100 + 235},
                 "brick wall, horizontal": 0xE100 + 247,
                 "brick wall, vertical": 0xE100 + 235,
                 "moss": (0xE100 + 256, 0xE100 + 236),
                 "weapons": {"club": 0xE100 + 67},
                 "ui_block_horizontal": 0xE100 + 688,
                 "ui_block_vertical": 0xE100 + 689,
                 "ui_block_nw": 0xE100 + 684,
                 "ui_block_ne": 0xE100 + 685,
                 "ui_block_sw": 0xE100 + 686,
                 "ui_block_se": 0xE100 + 687,
                 "indicator": 0xE100 + 671,
                 "indicator_2x2": 0xF500 + 671
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
                 "ui_block_horizontal": 0xE900 + 472,
                 "ui_block_vertical": 0xE900 + 440,
                 "ui_block_nw": 0xE900 + 468,
                 "ui_block_ne": 0xE900 + 468,
                 "ui_block_sw": 0xE900 + 468,
                 "ui_block_se": 0xE900 + 468,
                 "indicator": 0xE900 + 1746
                 }

    return tiles
