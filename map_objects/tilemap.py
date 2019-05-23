from bearlibterminal import terminal as blt
import variables


def init_tiles():

    tilesize = variables.tilesize + 'x' + variables.tilesize
    ui_size = variables.ui_size + 'x' + variables.ui_size

    # Load tilesets
    blt.set("U+E100: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=" + tilesize + ", resize-filter=nearest, align=top-left")
    blt.set("U+E900: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=" + ui_size + ", resize-filter=nearest, align=top-left")
    variables.tile_offset_x = int(
        int(variables.tilesize) / blt.state(blt.TK_CELL_WIDTH))
    variables.tile_offset_y = int(
        int(variables.tilesize) / blt.state(blt.TK_CELL_HEIGHT))
    variables.ui_offset_x = int(
        int(variables.ui_size) / blt.state(blt.TK_CELL_WIDTH))
    variables.ui_offset_y = int(
        int(variables.ui_size) / blt.state(blt.TK_CELL_HEIGHT))
    variables.camera_offset = int(variables.ui_size) / int(variables.tilesize)
    blt.clear()


def tilemap():
    tiles = {}
    if variables.gfx is "tiles":
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
                 "wall_brick": 0xE100 + 83,
                 "wall_moss": (0xE100 + 90, 0xE100 + 91, 0xE100 + 92),
                 "weapons": {"club": 0xE100 + 242}}

    elif variables.gfx is "ascii":
        tiles = {"tree": ("T", "t"),
                 "dead_tree": ("T", "t"),
                 "rocks": ("^"),
                 "ground_soil": ".",
                 "ground_moss": ".",
                 "floor": ".",
                 "rubble": ".",
                 "bones": ",",
                 "player": "@",
                 "player_remains": "@",
                 "monsters": {"rat": "r", "crow": "c", "snake": "s", "frog": "f"},
                 "monster_remains": "%",
                 "door": {"open": "-", "closed": "+", "locked": "*"},
                 "campfire": "¤",
                 "stairs": {"up": "<", "down": ">"},
                 "wall_brick": "#",
                 "wall_moss": "#",
                 "weapons": {"club": "\\"}}

    return tiles
