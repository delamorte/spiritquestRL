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
                 "ground_soil": 0xE100 + 21,
                 "floor": 0xE100 + 21,
                 "rubble": (0xE100 + 388, 0xE100 + 119),
                 "player": 0xE100 + 704,
                 "player_remains": 0xE100 + 468,
                 "monsters": {"rat": 0xE100 + 1416, "crow": 0xE100 + 1587, "snake": 0xE100 + 1097},
                 "monster_remains": 0xE100 + 513,
                 "door_closed": 0xE100 + 67,
                 "door_open": 0xE100 + 68,
                 "campfire": 0xE100 + 427,
                 "wall_brick": 0xE100 + 83,
                 "weapons":{"club": 0xE100 + 242}}

    elif variables.gfx is "ascii":
        tiles = {"tree": ("T", "t"),
                 "ground_soil": ".",
                 "floor": ".",
                 "rubble": ".",
                 "player": "@",
                 "player_remains": "[color=light red]@",
                 "monsters": {"rat": "r", "crow": "c", "snake": "s"},
                 "monster_remains": "%",
                 "door_closed": "+",
                 "door_open": "-",
                 "campfire": "¤",
                 "wall_brick": "#",
                 "weapons":{"club": "\\"}}

    return tiles

def bestiary():
    animals = {"crow": "quick, very agile, very weak, excellent vision",
               "rat": "very quick, agile, weak, poor vision",
               "snake": "strong, slow, average vision"}
    return animals