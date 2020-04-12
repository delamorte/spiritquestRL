from bearlibterminal import terminal as blt
from random import randint, random
import variables

dirt_colors = ["#402316", "#332925", "#4f3a28", "#4f3a28", "#3d342b", "#33221a", "#30170b", "#473c2b", "#332d16",
               "#361c18"]

mod_colors = ["gray",
              "dark gray",
              "dark gray",
              "darker gray",
              "darker gray",
              "darkest gray",
              "darkest gray"]


def get_dngn_colors(mod=0):
    color = dirt_colors[randint(0, len(dirt_colors) - 1)]
    if mod < 0:
        color = "#111111"
    if mod < -1:
        color = "#0e0f0f"
    if mod < -3:
        color = "#000000"

    return color


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
        name, color = name_color_from_ascii(value)
        return name, color
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
    elif value in range(54, 58 + 1) or value == 0xE700 + 107:
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
    elif value in range(102, 103 + 1) or value in range(0xE700 + 67, 0xE700 + 68 + 1):
        if value == 103 or value == 0xE700 + 68:
            name = "gate (open)"
        else:
            name = "gate (closed)"
        color = "gray"

    # Fences
    elif value in range(100, 111 + 1) or value == 0xE700 + 469:
        name = "fence"
        color = "dark gray"

    # Statues
    elif value in range(60, 64 + 1) or value == 0xE700 + 945:
        name = "statue"
        color = "gray"

    # Candles
    elif value == 70 or value == 0xE700 + 458:
        name = "candle"
        color = "amber"

    # Rocks & Rubble
    elif value == 132 or value == 133 or value == 0xE700 + 388 or value == 0xE700 + 119:
        name = "rubble"
        color = "dark gray"

    # Bones
    elif value in range(362, 366 + 1) or value in range(0xE700 + 468, 0xE700 + 471 + 1) or value == 0xE700 + 475:
        name = "bones"
        color = "gray"

    # Shrubs
    elif value in range(450, 452 + 1) or value in range(410, 412 + 1) or value == 430 or value == 432 \
            or value == 0xE700 + 93:
        name = "shrubs"
        if random() < 0.2:
            color = "darker amber"
        else:
            color = "darker green"

    elif value == 2 or value == 4 or value == 0xE700 + 20:
        name = "pavement"
        color = "darker gray"

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


def name_color_from_ascii(value):
    name, color = None, None

    # Coffins
    if value == "¤":
        name = "coffin"
        color = "darker amber"

    # Shrines
    elif value == "£":
        name = "shrine"
        if random() < 0.2:
            color = "bright yellow"
        else:
            color = None

    # Doors
    elif value == "-" or value == "+" or value == "*":
        if value == "-":
            name = "door (open)"
        elif value == "+":
            name = "door (closed)"
        else:
            name = "door (locked)"
        color = "darker amber"

    # Fences
    elif value == "|":
        name = "fence"
        color = "dark gray"

    # Statues
    elif value == "&":
        name = "statue"
        color = "gray"

    # Candles
    elif value == "!":
        name = "candle"
        color = "amber"

    # Rocks & Rubble
    elif value == "^":
        name = "rubble"
        color = "dark gray"

    # Bones
    elif value == ",":
        name = "bones"
        color = "gray"

    # Shrubs
    elif value == "`" or value == "´":
        name = "shrubs"
        if random() < 0.2:
            color = "darker amber"
        else:
            color = "darker green"

    elif value == ".":
        name = "floor"
        color = "darker gray"

    return name, color


def argb_from_color(col):
    return (col & 0xFF000000) >> 24, (col & 0xFF0000) >> 16, (col & 0xFF00) >> 8, col & 0xFF


def blend_colors(one, two):
    a1, r1, g1, b1 = argb_from_color(one)
    a2, r2, g2, b2 = argb_from_color(two)
    f = a2 / 255
    r = int(r1 * (1 - f) + r2 * f)
    g = int(g1 * (1 - f) + g2 * f)
    b = int(b1 * (1 - f) + b2 * f)
    return blt.color_from_argb(a1, r, g, b)
