from random import choice

import options
from data import json_data


def get_tile_object(name):
    if name in json_data.data.tiles:
        base_tile = json_data.data.tiles[name]
    else:
        base_tile = json_data.data.fighters[name]
    return base_tile


def get_tile(name, tile=None, state=None):
    if state is not None:
        if options.data.gfx == "ascii":
            state = "ascii_{0}".format(state)
            return tile[state]
        else:
            return int(tile["hex"], 0) + tile[state]
    if tile:
        base_tile = tile
    elif name in json_data.data.tiles:
        base_tile = json_data.data.tiles[name]
    else:
        base_tile = json_data.data.fighters[name]
    if options.data.gfx == "ascii":
        return base_tile["ascii"]
    tile = base_tile["tile"]
    hex_tile = int(base_tile["hex"], 0) + tile
    return hex_tile


def get_tile_variant(name, variant_idx=None, facing=None, variant_char=None, no_ascii=False):
    base_tile = json_data.data.tiles[name]
    if options.data.gfx == "ascii" and not no_ascii:
        variants = choice(base_tile["ascii_variants"]) if "ascii_variants" in base_tile.keys() else base_tile["ascii"]
        return variants
    variants = base_tile["tile_variants"]
    if not variants:
        return get_tile(name)
    if variant_idx is not None:
        tile = variants[variant_idx]
    elif base_tile["corners"] and facing is not None:
        tile = variants[facing]
    elif variant_char:
        tile = variant_char
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


def get_color(name, tile=None, mod=None, force_index=None, force_color=None):
    if force_color is not None:
        return force_color
    if tile:
        base_tile = tile
    else:
        if name in json_data.data.tiles:
            base_tile = json_data.data.tiles[name]
        elif name in json_data.data.fighters:
            base_tile = json_data.data.fighters[name]
        else:
            base_tile = {"colors": ["default"]}

    colors = base_tile["colors"]
    if force_index is not None:
        return colors[force_index]
    color = choice(colors)

    if mod and "hue" in base_tile.keys() and not base_tile["hue"]:
        # Pick random tone
        if mod > 0:
            color = (choice(["", "light", "lighter", "lightest"]) + " ").lstrip() + color
        elif mod == 0 or mod == -1:
            color = (choice(["", "dark", "light"]) + " ").lstrip() + color
        elif mod < -1:
            color = (choice(["", "dark", "darker"]) + " ").lstrip() + color

    return color


def get_tile_by_attribute(name, value):
    tile = None
    for k, v in json_data.data.tiles.items():
        if v[name] == value:
            tile = get_tile(k)
            return tile

    return tile


def get_tiles_by_attribute(name, value):
    tiles = []
    for k, v in json_data.data.tiles.items():
        if v[name] == value:
            tiles.append(k)

    return tiles


def get_fighters_by_attribute(name, value):
    """
    Get fighter name/char pairs based on attribute
    :param name: attribute name
    :param value: attribute value
    :return: fighters: return a list of tuples with name/char pairs
    """
    fighters = []
    for k, v in json_data.data.fighters.items():
        if v[name] == value:
            tile = get_tile(k)
            fighters.append((k, tile))

    return fighters
