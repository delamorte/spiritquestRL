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
                 "ground_soil": (0xE100 + 1748, 0xE100 + 1750),
                 "ground_moss": (0xE100 + 1751, 0xE100 + 1752, 0xE100 + 1753),
                 "floor": (0xE100 + 21, 0xE100 + 20, 0xE100 + 19),
                 "rubble": (0xE100 + 388, 0xE100 + 119),
                 "player": 0xE100 + 704,
                 "player_remains": 0xE100 + 468,
                 "monsters": {"rat": 0xE100 + 1416, "crow": 0xE100 + 1587, "snake": 0xE100 + 1097, "frog": 0xE100 + 1095},
                 "monster_remains": 0xE100 + 513,
                 "door": {"open": 0xE100 + 68, "closed": 0xE100 + 67},
                 "campfire": 0xE100 + 427,
                 "stairs": {"up": 0xE100 + 22, "down": 0xE100 + 27},
                 "wall_brick": 0xE100 + 83,
                 "wall_moss": (0xE100 + 90, 0xE100 + 91, 0xE100 + 92),
                 "weapons": {"club": 0xE100 + 242}}

    elif variables.gfx is "ascii":
        tiles = {"tree": ("T", "t"),
                 "ground_soil": ".",
                 "ground_moss": ".",
                 "floor": ".",
                 "rubble": ".",
                 "player": "@",
                 "player_remains": "@",
                 "monsters": {"rat": "r", "crow": "c", "snake": "s", "frog": "f"},
                 "monster_remains": "%",
                 "door": {"open": "-", "closed": "+"},
                 "campfire": "¤",
                 "stairs": {"up": "<", "down": ">"},
                 "wall_brick": "#",
                 "wall_moss": "#",
                 "weapons": {"club": "\\"}}

    return tiles


def bestiary():

    animals = {"crow": "quick, very agile, very weak, excellent vision",
               "rat": "very quick, agile, weak, small, poor vision",
               "snake": "strong, slow, small, average vision"}
    return animals


def abilities():
    # Abilities are organized in separate categories.
    # attack: ability name: [description, dmg, effect]
    abilities = {"attack":
                 {"poison bite": ["1d6, may poison", "1d6", "poison"],
                     "paralyzing bite": ["1d4, may paralyze", "1d5", "paralyze"],
                     "swoop": ["2d3, extra dmg on small targets", "2d3", ""]},

                 "move":
                 {"leap": "leap to a tile in a radius 4"},

                 "utility":
                 {"reveal": "reveal an area of radius 8 around you, may reveal secrets."}}
    return abilities
