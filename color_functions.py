from bearlibterminal import terminal as blt
from random import randint, random, choice

# BLT colors by name:
# grey (or gray), red, flame, orange,
# amber, yellow, lime, chartreuse, green,
# sea, turquoise, cyan, sky, azure, blue,
# han, violet, purple, fuchsia, magenta, pink,
# crimson, transparent

dirt_colors = ["#402316", "#4f3a28", "#4f3a28", "#33221a", "#30170b",
               "#361c18"]


def get_dngn_colors(mod=0):

    color = dirt_colors[randint(0, len(dirt_colors) - 1)]
    # if mod < 0:
    #     color = "#111111"
    # if mod < -1:
    #     color = "#0e0f0f"
    # if mod < -3:
    #     color = "#000000"

    return color


def get_terrain_colors(mod=None):
    colors = [
        "darker green",
        "dark green",
        "darker amber",
        "dark amber"
    ]

    if mod is None:
        mod = randint(0, len(colors) - 1)

    return colors[mod]


def get_flower_colors(mod=0):
    colors = []
    if mod > 0:
        colors = [(choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "orange",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "red",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "flame",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "amber",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "green",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "yellow",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "lime",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "chartreuse",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "violet",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "purple",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "pink",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "crimson",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "fuchsia",
                  (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + "sky"]

    if mod == 0 or mod == -1:
        colors = [(choice(["", "dark", "light"]) + " ").lstrip() + "orange",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "red",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "flame",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "amber",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "green",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "yellow",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "lime",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "chartreuse",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "violet",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "purple",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "pink",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "crimson",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "fuchsia",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "sky"]

    if mod < -1:
        colors = [(choice(["", "dark", "darker"]) + " ").lstrip() + "orange",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "red",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "flame",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "amber",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "green",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "yellow",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "lime",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "chartreuse",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "violet",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "purple",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "pink",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "crimson",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "fuchsia",
                  (choice(["", "dark", "darker"]) + " ").lstrip() + "sky"]
    return colors


def get_forest_colors(mod=0):
    # By name: grey (or gray), red, flame, orange, amber, yellow, lime, chartreuse, green, sea, turquoise, cyan,
    # sky, azure, blue, han, violet, purple, fuchsia, magenta, pink, crimson, transparent
    colors = []

    if mod > 0:
        colors = [(choice(["light", "lighter", "lightest"]) + " ").lstrip() + "orange",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "red",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "flame",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "amber",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "green",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "yellow",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "lime",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "chartreuse",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "violet",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "purple",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "pink",
                  (choice(["light", "lighter", "lightest"]) + " ").lstrip() + "crimson"]

    if mod < 0:
        colors = [(choice(["", "dark", "darker", "light"]) + " ").lstrip() + "orange",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "red",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "flame",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "amber",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "green",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "yellow",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "lime",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "chartreuse",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "violet",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "purple",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "pink",
                  (choice(["", "dark", "darker", "light"]) + " ").lstrip() + "crimson"]
    if mod == 0:
        colors = [(choice(["", "dark", "light"]) + " ").lstrip() + "orange",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "flame",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "amber",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "green",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "yellow",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "lime",
                  (choice(["", "dark", "light"]) + " ").lstrip() + "chartreuse"]
    return colors


def name_color_from_value(value, mod=0):

    name = None
    color = None

    # Coffins
    if value == 50 or value == 51:
        if value == 50:
            name = "coffin (closed)"
        else:
            name = "coffin (open)"
        color = "#856654"

    # Shrines
    elif value in range(54, 58 + 1):
        name = "shrine"
        if random() < 0.2:
            color = "bright yellow"
        else:
            color = None

    # Windows
    elif value == 182:
        name = "window"
        color = "darker gray"

    # Walls
    elif value in range(300, 306+1) or value == 280 or value == 217 or value in range(230, 232+1):
        name = "wall"
        color = "#2e2016"

    # Doors
    elif value in range(20, 38 + 1) or value == 327:
        doors_open = [21, 23, 25, 29, 31, 33, 35, 37]
        doors_closed = [20, 22, 24, 26, 27, 28, 30, 32, 36, 327]
        if value in doors_open:
            name = "door (open)"
        elif value in doors_closed:
            name = "door (closed)"
        else:
            name = "door"
        color = "darker amber"

    # Gates
    elif value in range(102, 103 + 1):
        if value == 103:
            name = "gate (open)"
        else:
            name = "gate (closed)"
        color = "gray"

    # Fences
    elif value in range(100, 111 + 1):
        fences_horizontal = [100, 101, 107, 106, 111, 110]
        if value in fences_horizontal:
            name = "fence, horizontal"
        else:
            name = "fence, vertical"
        color = "dark gray"

    # Campfires, symbols
    elif value == 16:
        name = "holy symbol"
        color = "lightest orange"

    elif value == 75:
        name = "cross"
        color = "gray"

    # Chairs etc
    elif value == 181:
        name = "throne"
        color = "dark gray"

    elif value == 163:
        name = "table"
        color = "#36200f"

    # Potions
    elif value in range(502, 504+1):
        name = "flask"
        colors = ["light red", "light green", "light sky"]
        color = colors[randint(0,2)]


    # Statues
    elif value in range(60, 64 + 1):
        name = "statue"
        color = "gray"

    # Candles
    elif value == 70 or value == 520:
        name = "candle"
        color = "amber"

    # Rocks & Rubble
    elif value == 132 or value == 133:
        name = "rubble"
        color = "dark gray"

    # Bones
    elif value in range(362, 366 + 1):
        name = "bones"
        color = "gray"

    elif value == 523:
        name = "skull"
        color = None

    # Books
    elif value in range (662, 666+1):
        name = "book"
        color = "#856654"

    # Shrubs
    elif value in range(450, 452 + 1) or value in range(410, 412 + 1) or value == 430 or value == 432:
        name = "shrubs"
        if random() < 0.2:
            color = "darker amber"
        else:
            color = "darker green"

    # Plants, flowers
    elif value in range(120, 123+1) or value in range(399, 401+1):
        name = "plants"
        colors = get_forest_colors(mod)
        color = colors[randint(0, len(colors)-1)]

    elif value in range(127, 129+1):
        name = "flowers"
        colors = get_flower_colors(mod)
        color = colors[randint(0, len(colors)-1)]

    elif value == 131:
        name = "mushrooms"
        color = dirt_colors[randint(0, len(dirt_colors)-1)]

    elif value == 2 or value == 4:
        name = "pavement"
        color = "darkest gray"

    elif value == 253:
        name = "floor"
        color = "darkest gray"

    elif value == 277:
        name = "floor"
        color = None

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
              "bone snake": "default",
              "chaos dog": "light azure",
              "bat": "light #856654",
              "imp": "red",
              "leech": "dark pink",
              "spirit": "lightest azure",
              "chaos spirit": "dark orange",
              "ghost dog": "default",
              "gecko": "dark green",
              "serpent": "violet",
              "fairy": "light violet",
              "keeper of dreams": "flame"}
    if name not in colors:
        color = "amber"
    else:
        color = colors[name]

    return color


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
