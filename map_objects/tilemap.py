from random import choice, randint
import options
from data import json_data


def get_tile_object(name):
    base_tile = json_data.data.tiles[name]
    return base_tile


def get_tile(name, tile=None):
    if tile:
        base_tile = tile
    else:
        base_tile = json_data.data.tiles[name]
    if options.data.gfx == "ascii":
        return base_tile["ascii"]
    tile = base_tile["tile"]
    hex_tile = int(base_tile["hex"], 0) + tile
    return hex_tile


def get_tile_variant(name, variant, no_ascii=False):
    base_tile = json_data.data.tiles[name]
    if options.data.gfx == "ascii" and not no_ascii:
        return base_tile["ascii"]
    variants = base_tile["tile_variants"]
    if not variants:
        return base_tile
    if variant:
        tile = variants[variant]
    else:
        tile = choice(variants)
    hex_tile = int(base_tile["hex"], 0) + tile
    return hex_tile


def get_tile_by_value(value):
    for k, v in json_data.data.tiles.items():
        if v["tile"] == value:
            return k
        elif value in v["tile_variants"]:
            return k

    return None


def get_color(name, tile=None, mod=None):
    if tile:
        base_tile = tile
    else:
        base_tile = json_data.data.tiles[name]

    colors = base_tile["colors"]
    color = choice(colors)

    if mod and "shaded" in base_tile.keys() and not base_tile["shaded"]:
        # Pick random tone
        if mod > 0:
            color = (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + color
        elif mod == 0 or mod == -1:
            color = (choice(["", "dark", "light"]) + " ").lstrip() + color
        elif mod < -1:
            color = (choice(["", "dark", "darker"]) + " ").lstrip() + color

    return color
