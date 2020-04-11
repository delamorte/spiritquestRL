from random import randint, random
import variables

def get_dngn_colors(mod):
    colors = []
    if mod >= 0:
        colors = ["lightest amber",
                  "lighter amber",
                  "light amber",
                  "dark amber",
                  "darker amber",
                  "darkest gray"]

    if mod < 0:
        colors = ["lightest gray",
                  "lighter gray",
                  "light gray",
                  "dark gray",
                  "darker gray",
                  "darkest gray"]

    # if mod > 0:
    #    colors = [None,
    #                     None,
    #                     None,
    #                     None,
    #                     None,
    #                     None]

    return colors


def get_terrain_colors(mod=None):
    colors = [
        "darker green",
        "darkest green",
        "darker amber",
        "darkest amber"
    ]

    if mod is None:
        mod = randint(0, len(colors) - 1)

    return colors[mod]


def get_forest_colors(mod=-1):
    colors = []
    if mod > 0:
        colors = ["lightest orange",
                  "lighter orange",
                  "light orange",
                  "light green",
                  "light amber"]

    if mod < 0:
        colors = ["darkest amber",
                  "darker gray",
                  "dark gray",
                  "darker green",
                  "darkest green"]
    if mod == 0:
        colors = ["lightest green",
                  "lighter green",
                  "light green",
                  "dark green",
                  "darker green",
                  "darkest green"]
    return colors


def name_color_from_value(value, tileset=0xE500):
    if isinstance(value, str):
        return value, None
    elif value < 1000:
        tileset = 0
    name = None
    color = None
    if variables.gfx != "tiles":
        value -= tileset


    # Coffins
    if value == 50 or value == 51 or value == 0xE700 + 158:
        name = "coffin"
        color = "darker amber"

    # Shrines
    elif value in range(54, 58 + 1) or value == 0xE700+107:
        name = "shrine"
        if random() < 0.2:
            color = "bright yellow"
        else:
            color = None

    # Doors
    elif value in range(20, 38 + 1):
        name = "door"
        color = "darker amber"

    # Gates
    elif value in range(102, 103 + 1) or value in range (0xE700+67, 0xE700+68+1):
        if value == 103 or value == 0xE700+68:
            name = "gate (open)"
        else:
            name = "gate (closed)"
        color = "gray"

    # Fences
    elif value in range(100, 111 + 1) or value == 0xE700 + 83:
        name = "fence"
        color = "dark gray"

    # Statues
    elif value in range(60, 64 + 1) or value == 0xE700+945:
        name = "statue"
        color = "gray"

    # Candles
    elif value == 70 or value == 0xE700+458:
        name = "candle"
        color = "amber"

    # Rocks & Rubble
    elif value == 412 or value == 411 or value == 0xE700 + 388 or value == 0xE700 + 119:
        name = "rubble"
        color = "dark gray"

    # Bones
    elif value in range(362, 366+1) or value in range(0xE700 + 468, 0xE700 + 471+1) or value == 0xE700 + 475:
        name = "bones"
        color = "gray"

    elif value in range(450, 452+1) or value in range(410, 412+1) or value == 430 or value == 432\
            or value == 0xE700+93:
        name = "shrubs"
        if random() < 0.2:
            color = "darker green"
        else:
            color = "darkest amber"

    return name, color


def get_monster_color(name):
    colors = {"rat": "#856654",
              "crow": "darker azure",
              "snake": "yellow",
              "frog": "green",
              "bear": "#856654",
              "felid": "lighter blue",
              "mosquito": "pink",
              "chaos cat": "dark red",
              "chaos bear": "dark amber",
              "cockroach": "dark amber",
              "bone snake": None,
              "chaos dog": "light azure",
              "bat": "light #856654",
              "imp": "red",
              "leech": "dark pink",
              "spirit": "lightest azure",
              "chaos spirit": "dark orange",
              "ghost dog": None,
              "gecko": "dark green",
              "serpent": "violet",
              "fairy": "light violet"}

    return colors[name]
