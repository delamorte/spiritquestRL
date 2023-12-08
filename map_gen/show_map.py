# coding=utf-8

from __future__ import division

from ctypes import c_uint32, addressof

import numpy as np
from bearlibterminal import terminal as blt


def test_dynamic_sprites(game_map, ui_elements, options):
    x0 = y0 = 1
    view_height, view_width = ui_elements.screen_borders.h-1, ui_elements.screen_borders.w-1

    def make_minimap():

        minimap = np.ones_like(game_map.tiles, dtype=np.int32)
        for x in range(game_map.width):
            for y in range(game_map.height):
                minimap[y][x] = blt.color_from_name("dark gray")
                if len(game_map.tiles[x][y].entities_on_tile) > 0:
                    if game_map.tiles[x][y].entities_on_tile[-1].name == "tree":
                        minimap[y][x] = blt.color_from_name("dark green")
                    elif "wall" in game_map.tiles[x][y].entities_on_tile[-1].name:
                        minimap[y][x] = blt.color_from_name("dark amber")
                    elif game_map.tiles[x][y].entities_on_tile[-1].name == "player":
                        minimap[y][x] = blt.color_from_name(None)
                    elif game_map.tiles[x][y].entities_on_tile[-1].fighter \
                            and game_map.tiles[x][y].entities_on_tile[-1].name != "player":
                        minimap[y][x] = blt.color_from_name("light red")
                    else:
                        minimap[y][x] = blt.color_from_name("light gray")
                elif game_map.tiles[x][y].blocked:
                    minimap[y][x] = blt.color_from_name("light gray")
                # if not game_map.tiles[x][y].explored:
                #     minimap[y][x] = blt.color_from_name("#000000")

        minimap = minimap.flatten()
        minimap = (c_uint32 * len(minimap))(*minimap)
        blt.set(
            "U+F900: %d, raw-size=%dx%d, resize=%dx%d, resize-filter=nearest" % (
                addressof(minimap),
                game_map.width, game_map.height,
                500, 500)
        )

    while True:
        blt.clear()

        make_minimap()
        blt.color("white")
        #blt.put_ext(view_width * 4 + 1, 0, margin, margin, 0xF900)
        blt.put(x0 * options.data.tile_offset_x + 3, y0 * options.data.tile_offset_y + 3, 0xF900)
        #blt.puts(1, view_height * 2 + 1, "[color=orange]Tip:[/color] use arrow keys to move viewport over the map")

        blt.refresh()

        key = blt.read()

        if key in (blt.TK_CLOSE, blt.TK_ESCAPE, blt.TK_TAB):
            blt.clear()
            break