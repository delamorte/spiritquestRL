from random import randint

from bearlibterminal import terminal as blt


# BLT colors by name:
# grey (or gray), red, flame, orange,
# amber, yellow, lime, chartreuse, green,
# sea, turquoise, cyan, sky, azure, blue,
# han, violet, purple, fuchsia, magenta, pink,
# crimson, transparent


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


def random_color():
    a = 255
    r = randint(1, 255)
    g = randint(1, 255)
    b = randint(1, 255)
    color = blt.color_from_argb(a, r, g, b)
    return color
