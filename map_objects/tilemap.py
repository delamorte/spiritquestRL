import options


def tilemap():
    tiles = {}
    if options.gfx is "tiles":
        tiles = {"tree": (0xE100 + 87, 0xE100 + 88, 0xE100 + 89, 0xE100 + 93, 0xE100 + 94, 0xE100 + 95),
                 "ground_soil": 0xE100 + 21,
                 "floor": 0xE100 + 21,
                 "player": 0xE100 + 704,
                 "player_remains": 0xE100 + 468,
                 "monsters": {"cat": 0xE100 + 1252, "crow": 0xE100 + 1587, "snake": 0xE100 + 1097},
                 "monster_remains": 0xE100 + 513,
                 "door_closed": 0xE100 + 67,
                 "door_open": 0xE100 + 68,
                 "campfire": 0xE100 + 427,
                 "wall_brick": 0xE100 + 83}

    elif options.gfx is "ascii":
        tiles = {"tree": ("T", "t"),
                 "ground_soil": ".",
                 "floor": ".",
                 "player": "@",
                 "player_remains": "@",
                 "monsters": {"cat": "C", "crow": "c", "snake": "S"},
                 "monster_remains": "%",
                 "door_closed": "+",
                 "door_open": "-",
                 "campfire": "¤",
                 "wall_brick": "#"}

    return tiles