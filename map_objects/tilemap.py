from bearlibterminal import terminal as blt
import variables
import xml.etree.ElementTree as ET


def init_tiles():

    tilesize = variables.tile_width + 'x' + variables.tile_height

    # Load tilesets
    blt.set("U+E100: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=" + tilesize + ", resize-filter=nearest, align=top-left")

    # Oryx set
    blt.set("U+E200: ./tilesets/oryx_roguelike_2.0/V1/oryx_roguelike_16x24_trans.png, \
        size=16x24, resize=" + "32x48" + ", resize-filter=nearest, spacing=4x4, align=top-left")

    # Oryx terrain+objects
    blt.set("U+F100: ./tilesets/oryx_roguelike_2.0/terrain_objects_comb.png, \
        size=16x24, resize=" + "32x48" + ", resize-filter=nearest, spacing=4x4, align=top-left")

    variables.tile_offset_x = int(
        int(variables.tile_width) / blt.state(blt.TK_CELL_WIDTH))
    variables.tile_offset_y = int(
        int(variables.tile_height) / blt.state(blt.TK_CELL_HEIGHT))

    blt.clear()

def tilemap():
    tiles = {}
    if variables.gfx == "tiles":
        tiles = {"tree": (0xE100 + 87, 0xE100 + 88, 0xE100 + 89, 0xE100 + 93, 0xE100 + 94, 0xE100 + 95),
                 "dead_tree": (0xE100 + 112, 0xE100 + 144),
                 "rocks": (0xE100 + 1726, 0xE100 + 1727),
                 "ground_soil": (0xE100 + 1748, 0xE100 + 1750),
                 "ground_moss": (0xE100 + 1751, 0xE100 + 1752, 0xE100 + 1753),
                 "floor": (0xE100 + 21, 0xE100 + 20, 0xE100 + 19),
                 "rubble": (0xE100 + 388, 0xE100 + 119),
                 "bones": (0xE100 + 468, 0xE100 + 469, 0xE100 + 470, 0xE100 + 471, 0xE100 + 475),
                 "player": 0xE100 + 704,
                 "player_remains": 0xE100 + 468,
                 "monsters": {"rat": 0xE100 + 1416,
                              "bear": 0xE100 + 1780,
                              "crow": 0xE100 + 1587,
                              "felid": 0xE100 + 1252,
                              "snake": 0xE100 + 1097,
                              "frog": 0xE100 + 1095,
                              "mosquito": 0xE100 + 1554},
                 "monsters_chaos": {"rat": 0xE100 + 1416,
                                    "crow": 0xE100 + 1587,
                                    "chaos cat": 0xE100 + 1255,
                                    "chaos bear": 0xE100 + 1553,
                                    "chaos spirit": 0xE100 + 1029,
                                    "cockroach": 0xE100 + 1473,
                                    "bone snake": 0xE100 + 1093,
                                    "chaos dog": 0xE100 + 960,
                                    "bat": 0xE100 + 1200,
                                    "imp": 0xE100 + 1047,
                                    "leech": 0xE100 + 1204},
                 "monsters_light": {"bear": 0xE100 + 1780,
                                    "crow": 0xE100 + 1587,
                                    "spirit": 0xE100 + 1017,
                                    "ghost dog": 0xE100 + 959,
                                    "snake": 0xE100 + 1100,
                                    "gecko": 0xE100 + 1104,
                                    "serpent": 0xE100 + 1323,
                                    "frog": 0xE100 + 1095,
                                    "mosquito": 0xE100 + 1554,
                                    "fairy": 0xE100 + 1032},

                 "unique_monsters": {"king kobra": 0xE100 + 1105, "albino rat": 0xE100 + 1414},
                 "monster_remains": 0xE100 + 513,
                 "door": {"open": 0xE100 + 68, "closed": 0xE100 + 67, "locked": 0xE100 + 78},
                 "campfire": 0xE100 + 427,
                 "stairs": {"up": 0xE100 + 22, "down": 0xE100 + 27},
                 "brick": {"horizontal": 0xE100 + 247, "vertical": 0xE100 + 235},
                 "moss": (0xE100 + 90, 0xE100 + 91, 0xE100 + 92),
                 "weapons": {"club": 0xE100 + 242}}

    elif variables.gfx == "oryx":
        tiles = {"tree": (0xE200 + 399, 0xE200 + 400, 0xE200 + 401, 0xE200 + 402, 0xE200 + 405),
                 "dead_tree": (0xE200 + 403, 0xE200 + 404),
                 "rocks": (0xE200 + 412,),
                 "ground_soil": (0xE200 + 186,),
                 "ground_moss": (0xE200 + 186,),
                 "ground_dot": (0xE200 + 293),
                 "floor": (0xE200 + 237,),
                 "rubble": (0xE200 + 411,),
                 "bones": (0xE200 + 362, 0xE200 + 363, 0xE200 + 364, 0xE200 + 365, 0xE200 + 366),
                 "player": 0xE200 + 460,
                 "player_remains": 0xE200 + 379,
                 "monsters": {"rat": 0xE200 + 495,
                              "bear": 0xE200 + 526,
                              "crow": 0xE200 + 509,
                              "felid": 0xE200 + 505,
                              "snake": 0xE200 + 502,
                              "frog": 0xE200 + 504,
                              "mosquito": 0xE200 + 524},
                 "monsters_chaos": {"rat": 0xE200 + 498,
                                    "crow": 0xE200 + 509,
                                    "chaos cat": 0xE200 + 506,
                                    "chaos bear": 0xE200 + 529,
                                    "chaos spirit": 0xE200 + 638,
                                    "cockroach": 0xE200 + 517,
                                    "bone snake": 0xE200 + 511,
                                    "chaos dog": 0xE200 + 499,
                                    "bat": 0xE200 + 500,
                                    "imp": 0xE200 + 555,
                                    "leech": 0xE200 + 614},
                 "monsters_light": {"bear": 0xE200 + 528,
                                    "crow": 0xE200 + 509,
                                    "spirit": 0xE200 + 636,
                                    "ghost dog": 0xE200 + 605,
                                    "snake": 0xE200 + 502,
                                    "gecko": 0xE200 + 503,
                                    "serpent": 0xE200 + 512,
                                    "frog": 0xE200 + 504,
                                    "mosquito": 0xE200 + 524,
                                    "fairy": 0xE200 + 579},

                 "unique_monsters": {"king kobra": 0xE200 + 602, "albino rat": 0xE200 + 498},
                 "monster_remains": 0xE200 + 373,
                 "door": {"open": 0xE200 + 307, "closed": 0xE200 + 306, "locked": 0xE200 + 308},
                 "campfire": 0xE200 + 303,
                 "stairs": {"up": 0xE200 + 324, "down": 0xE200 + 323},
                 # Walls
                 "brick": {"horizontal": 0xE200 + 247, "vertical": 0xE200 + 235},
                 "moss": (0xE200 + 256, 0xE200 + 236),
                 "weapons": {"club": 0xE200 + 67}}

    elif variables.gfx == "ascii":
        tiles = {"tree": ("T", "t"),
                 "dead_tree": ("T", "t"),
                 "rocks": ("^"),
                 "ground_soil": ".",
                 "ground_moss": ".",
                 "ground_dot": ".",
                 "floor": ".",
                 "rubble": ".",
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
                 "campfire": "¤",
                 "stairs": {"up": "<", "down": ">"},
                 "brick": {"horizontal": "#", "vertical": "#"},
                 "moss": "#",
                 "weapons": {"club": "\\"}}

    return tiles
