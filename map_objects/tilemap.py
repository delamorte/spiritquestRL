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
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx2), 320, 600) +
            tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

    blt.set("U+E700: %d, \
        size=16x16, raw-size=%dx%d, resize=" % (addressof(gfx3), 512, 960) +
            tilesize + ", resize-filter=nearest, align=top-left")

    blt.set("U+F100: %d, \
        size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
            "32x48" + ", resize-filter=nearest, spacing=4x4, align=top-left")

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

def tilemap():
    tiles = {}
    if variables.gfx == "tiles":
        tiles = {"tree": (0xE700 + 87, 0xE700 + 88, 0xE700 + 89, 0xE700 + 93, 0xE700 + 94, 0xE700 + 95),
                 "dead_tree": (0xE700 + 112, 0xE700 + 144),
                 "rocks": (0xE700 + 1726, 0xE700 + 1727),
                 "coffin": 0xE700 + 158,
                 "shrine": 0xE700 + 107,
                 "candle": 0xE700 + 458,
                 "gate": {"open": 0xE700 + 68, "closed": 0xE700 + 67, "locked": 0xE700 + 78},
                 "gate (open)": 0xE700 + 68,
                 "gate (closed)": 0xE700 + 67,
                 "fence": 0xE700 + 469,
                 "statue": 0xE700 + 945,
                 "shrubs": 0xE700 + 93,
                 "ground_dot": (0xE700 + 1748),
                 "ground_soil": (0xE700 + 1748, 0xE700 + 1750),
                 "ground_moss": (0xE700 + 1751, 0xE700 + 1752, 0xE700 + 1753),
                 "floor": (0xE700 + 20, 0xE700 + 19, 0xE700 + 19),
                 "floor_wood": 0xE700 + 21,
                 "pavement": (0xE700 + 20),
                 "rubble": (0xE700 + 388, 0xE700 + 119),
                 "bones": (0xE700 + 468, 0xE700 + 469, 0xE700 + 470, 0xE700 + 471, 0xE700 + 475),
                 "player": 0xE700 + 704,
                 "player_remains": 0xE700 + 468,
                 "monsters": {"rat": 0xE700 + 1416,
                              "bear": 0xE700 + 1780,
                              "crow": 0xE700 + 1587,
                              "felid": 0xE700 + 1252,
                              "snake": 0xE700 + 1097,
                              "frog": 0xE700 + 1095,
                              "mosquito": 0xE700 + 1554},
                 "monsters_chaos": {"rat": 0xE700 + 1416,
                                    "crow": 0xE700 + 1587,
                                    "chaos cat": 0xE700 + 1255,
                                    "chaos bear": 0xE700 + 1553,
                                    "chaos spirit": 0xE700 + 1029,
                                    "cockroach": 0xE700 + 1473,
                                    "bone snake": 0xE700 + 1093,
                                    "chaos dog": 0xE700 + 960,
                                    "bat": 0xE700 + 1200,
                                    "imp": 0xE700 + 1047,
                                    "leech": 0xE700 + 1204},
                 "monsters_light": {"bear": 0xE700 + 1780,
                                    "crow": 0xE700 + 1587,
                                    "spirit": 0xE700 + 1017,
                                    "ghost dog": 0xE700 + 959,
                                    "snake": 0xE700 + 1100,
                                    "gecko": 0xE700 + 1104,
                                    "serpent": 0xE700 + 1323,
                                    "frog": 0xE700 + 1095,
                                    "mosquito": 0xE700 + 1554,
                                    "fairy": 0xE700 + 1032},

                 "unique_monsters": {"king kobra": 0xE700 + 1105, "albino rat": 0xE700 + 1414},
                 "monster_remains": 0xE700 + 513,
                 "door": {"open": 0xE700 + 68, "closed": 0xE700 + 67, "locked": 0xE700 + 78},
                 "campfire": 0xE700 + 427,
                 "stairs": {"up": 0xE700 + 22, "down": 0xE700 + 27},
                 "brick": {"horizontal": 0xE700 + 83, "vertical": 0xE700 + 83},
                 "moss": (0xE700 + 90, 0xE700 + 91, 0xE700 + 92),
                 "weapons": {"club": 0xE700 + 242},
                 "ui_block_horizontal": 0xE700 + 472,
                 "ui_block_vertical": 0xE700 + 440,
                 "ui_block_nw": 0xE700 + 468,
                 "ui_block_ne": 0xE700 + 468,
                 "ui_block_sw": 0xE700 + 468,
                 "ui_block_se": 0xE700 + 468,
                 "indicator": 0xE700 + 1746
                 }

    elif variables.gfx == "oryx":
        tiles = {"tree": (0xE100 + 399, 0xE100 + 400, 0xE100 + 401, 0xE100 + 402, 0xE100 + 405),
                 "dead_tree": (0xE100 + 403, 0xE100 + 404),
                 "rocks": (0xE500 + 133,),
                 "coffin": {"open": 0xE100 + 50, "closed": 0xE700 + 151},
                 "shrine": (0xE100 + 55, 0xE100 + 56, 0xE100 + 57, 0xE100 + 58),
                 "candle": 0xE100 + 70,
                 "gate": {"open": 0xE100 + 103, "closed": 0xE700 + 102, "locked": 0xE700 + 102},
                 "fence": (0xE100 + 107, 0xE100 + 101),
                 "statue": (0xE100 + 61, 0xE100 + 62, 0xE100 + 63, 0xE100 + 64),
                 "ground_soil": (0xE100 + 692,),
                 "ground_moss": (0xE100 + 186,),
                 "ground_dot": (0xE100 + 293),
                 "floor": (0xE100 + 237,),
                 "floor_wood": 0xE100 + 264,
                 "rubble": (0xE500 + 132,),
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

                 "unique_monsters": {"king kobra": 0xE100 + 602, "albino rat": 0xE100 + 498},
                 "monster_remains": 0xE100 + 373,
                 "door": {"open": 0xE100 + 307, "closed": 0xE100 + 306, "locked": 0xE100 + 308},
                 "campfire": 0xE100 + 303,
                 "stairs": {"up": 0xE100 + 324, "down": 0xE100 + 323},
                 # Walls
                 "brick": {"horizontal": 0xE100 + 247, "vertical": 0xE100 + 235},
                 "moss": (0xE100 + 256, 0xE100 + 236),
                 "weapons": {"club": 0xE100 + 67},
                 "ui_block_horizontal": 0xE100 + 688,
                 "ui_block_vertical": 0xE100 + 689,
                 "ui_block_nw": 0xE100 + 684,
                 "ui_block_ne": 0xE100 + 685,
                 "ui_block_sw": 0xE100 + 686,
                 "ui_block_se": 0xE100 + 687,
                 "indicator": 0xE100 + 671
                 }

    elif variables.gfx == "ascii":
        tiles = {"tree": ("T", "t"),
                 "dead_tree": ("T", "t"),
                 "rocks": "^",
                 "coffin": "¤",
                 "shrine": "£",
                 "candle": "!",
                 "gate": {"open": "-", "closed": "+", "locked": "*"},
                 "gate (open)": "-",
                 "gate (closed)": "+",
                 "fence": "|",
                 "statue": "&",
                 "ground_soil": ".",
                 "ground_moss": ".",
                 "ground_dot": ".",
                 "floor": ".",
                 "floor_wood": ".",
                 "pavement": ".",
                 "rubble": ".",
                 "shrubs": ("`", "´"),
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

                 "unique_monsters": {"king kobra": "K", "albino rat": "R"},
                 "monster_remains": "%",
                 "door": {"open": "-", "closed": "+", "locked": "*"},
                 "campfire": "æ",
                 "stairs": {"up": "<", "down": ">"},
                 "brick": {"horizontal": "#", "vertical": "#"},
                 "moss": "#",
                 "weapons": {"club": "\\"},
                 "ui_block_horizontal": 0xE700 + 472,
                 "ui_block_vertical": 0xE700 + 440,
                 "ui_block_nw": 0xE700 + 468,
                 "ui_block_ne": 0xE700 + 468,
                 "ui_block_sw": 0xE700 + 468,
                 "ui_block_se": 0xE700 + 468,
                 "indicator": 0xE700 + 1746
                 }

    return tiles


def convert_tileset(value):
    name, _ = name_color_from_value(value)
    converted_value = tilemap()[name]
    # if variables.gfx == "ascii":
    #     converted_value = ord(converted_value)

    return converted_value
