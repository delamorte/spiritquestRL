from bearlibterminal import terminal as blt
from collections import Counter
from helpers import get_article
from math import ceil
from textwrap import shorten
import numpy as np
from map_objects.tilemap import tilemap, tilemap_ui
from scipy.spatial.distance import cityblock
import variables
from palettes import argb_from_color
import random


def draw(entity, game_map, x, y, player):
    # if variables.gfx == "adambolt" and entity.fighter:
    #     blt.layer(0)
    #     blt.color("lighter amber")
    #     blt.put(x * variables.tile_offset_x, y *
    #             variables.tile_offset_y, 0xE900 + 3)

    # Draw the entity to the screen
    blt.layer(entity.layer)
    blt.color(entity.color)
    c = blt.color_from_name(entity.color)
    if variables.gfx == "adambolt":
        c = blt.color_from_name(None)
    if not entity.cursor:
        light_map = player.player.lightmap
        argb = argb_from_color(c)
        a = argb[0]
        r = min(int(argb[1] * light_map[entity.y][entity.x]), 255)
        g = min(int(argb[2] * light_map[entity.y][entity.x]), 255)
        b = min(int(argb[3] * light_map[entity.y][entity.x]), 255)

        blt.color(blt.color_from_argb(a, r, g, b))

    if not (player.light_source.fov_map.fov[entity.y, entity.x] and
            game_map.tiles[entity.x][entity.y].explored):
        blt.color("dark gray")

    # Cursor needs some offset in ascii
    if variables.gfx == "ascii" and entity.name == "cursor":
        blt.put_ext(x * variables.tile_offset_x, y *
                    variables.tile_offset_y, -3 * variables.tile_offset_x, -5 * variables.tile_offset_y, entity.char)
    else:
        if entity.boss and not entity.fighter:
            blt.put((x - 1) * variables.tile_offset_x, (y - 1) *
                    variables.tile_offset_y, entity.char)
        else:
            blt.put(x * variables.tile_offset_x, y *
                    variables.tile_offset_y, entity.char)


def draw_entities(entities, player, game_map, game_camera, cursor_x, cursor_y):
    light_sources = []
    for entity in entities:

        x, y = game_camera.get_coordinates(entity.x, entity.y)

        if entity.x == player.x and entity.y == player.y and entity.stand_on_messages:

            variables.stack.append(get_article(
                entity.name).capitalize() + " " + entity.name)
            if entity.xtra_info:
                variables.stack.append(entity.xtra_info)

        if cursor_x is not None:
            if entity.occupied_tiles is not None:
                if (game_map.tiles[entity.x][entity.y].explored and not entity.cursor and
                        (cursor_x, cursor_y) in entity.occupied_tiles):

                    variables.stack.append(get_article(entity.name).capitalize() + " " + entity.name)
                    variables.stack.append(str("x: " + (str(cursor_x) + ", y: " + str(cursor_y))))

                    if entity.xtra_info:
                        variables.stack.append(entity.xtra_info)

                    if entity.fighter:
                        draw_stats(player, entity)

            elif (entity.x == cursor_x and entity.y == cursor_y and not
            entity.cursor and game_map.tiles[entity.x][entity.y].explored):

                variables.stack.append(get_article(entity.name).capitalize() + " " + entity.name)
                variables.stack.append(str("x: " + (str(cursor_x) + ", y: " + str(cursor_y))))

                if entity.xtra_info:
                    variables.stack.append(entity.xtra_info)

                if entity.fighter:
                    draw_stats(player, entity)

            if entity.name == "cursor":
                clear(entity, entity.last_seen_x, entity.last_seen_y)
                draw(entity, game_map, x, y, player)

        if not entity.cursor and player.light_source.fov_map.fov[entity.y, entity.x]:
            # why is this here? causes rendering bugs!!!
            # clear(entity, entity.last_seen_x, entity.last_seen_y)

            if not entity.player and not entity.cursor:
                entity.last_seen_x = entity.x
                entity.last_seen_y = entity.y

            if entity.player or entity.fighter:
                draw(entity, game_map, x, y, player)
            elif not entity.light_source:
                draw(entity, game_map, x, y, player)
            else:
                light_sources.append(entity.light_source)
                continue

        elif (not player.light_source.fov_map.fov[entity.y, entity.x] and
              game_map.tiles[entity.last_seen_x][entity.last_seen_y].explored and not
              player.light_source.fov_map.fov[entity.last_seen_y, entity.last_seen_x]):

            x, y = game_camera.get_coordinates(entity.last_seen_x, entity.last_seen_y)

            # what is this if???????
            # if (ceil(variables.camera_offset) < x < game_camera.width - ceil(variables.camera_offset) and ceil(
            #        variables.camera_offset) < y < game_camera.height - ceil(variables.camera_offset)):
            if entity.light_source and not entity.fighter:
                light_sources.append(entity.light_source)
            else:
                draw(entity, game_map, x, y, player)

        if player.light_source.fov_map.fov[entity.y, entity.x] and entity.ai and variables.gfx != "ascii":
            draw_indicator(player.x, player.y, game_camera, "gray")
            draw_indicator(entity.x, entity.y, game_camera, "dark red", entity.occupied_tiles)

    return light_sources


def draw_map(game_map, game_camera, player, cursor_x, cursor_y):
    # Set boundaries where to draw map
    bound_x = ceil(variables.camera_offset)
    bound_y = ceil(variables.camera_offset)
    bound_x2 = game_camera.width - ceil(variables.camera_offset)
    bound_y2 = game_camera.height - ceil(variables.camera_offset)
    # Clear what's drawn in camera
    clear_camera(5)
    # Set boundaries if map is smaller than viewport
    if game_map.width < game_camera.width:
        bound_x2 = game_map.width
    if game_map.height < game_camera.height:
        bound_y2 = game_map.height
    # Draw all the tiles within the boundaries of the game camera
    center = np.array([player.y, player.x])
    entities = []
    for y in range(bound_y, bound_y2):
        for x in range(bound_x, bound_x2):
            map_x, map_y = game_camera.x + x, game_camera.y + y
            if game_map.width < game_camera.width:
                map_x = x
            if game_map.height < game_camera.height:
                map_y = y
            visible = player.light_source.fov_map.fov[map_y, map_x]

            # Draw tiles within fov
            if visible:
                blt.layer(0)
                dist = float(cityblock(center, np.array([map_y, map_x])))
                light_level = game_map.tiles[map_x][map_y].natural_light_level * \
                              (1.0 / (1.05 + 0.035 * dist + 0.025 * dist * dist))
                player.player.lightmap[map_y][map_x] = light_level

                c = blt.color_from_name(game_map.tiles[map_x][map_y].color)
                if variables.gfx == "adambolt":
                    c = blt.color_from_name("gray")
                argb = argb_from_color(c)
                a = argb[0]
                r = min(int(argb[1] * light_level), 255)
                g = min(int(argb[2] * light_level), 255)
                b = min(int(argb[3] * light_level), 255)
                blt.color(blt.color_from_argb(a, r, g, b))

                blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                        game_map.tiles[map_x][map_y].char)

                if len(game_map.tiles[map_x][map_y].layers) > 0:
                    i = 1
                    for tile in game_map.tiles[map_x][map_y].layers:
                        blt.layer(i)
                        c = blt.color_from_name(tile[1])
                        argb = argb_from_color(c)
                        a = argb[0]
                        r = min(int(argb[1] * light_level), 255)
                        g = min(int(argb[2] * light_level), 255)
                        b = min(int(argb[3] * light_level), 255)
                        blt.color(blt.color_from_argb(a, r, g, b))
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                tile[0])
                        i += 1

                # Set everything in fov as explored
                game_map.tiles[map_x][map_y].explored = True

            # Gray out explored tiles
            elif game_map.tiles[map_x][map_y].explored:
                blt.layer(0)
                blt.color("darkest gray")
                blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                        game_map.tiles[map_x][map_y].char)
                if len(game_map.tiles[map_x][map_y].layers) > 0:
                    i = 1
                    for tile in game_map.tiles[map_x][map_y].layers:
                        blt.layer(i)
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                tile[0])
                        i += 1

            if len(game_map.tiles[map_x][map_y].entities_on_tile) > 0:
                for n in game_map.tiles[map_x][map_y].entities_on_tile:
                    if n not in entities:
                        entities.append(n)

    light_sources = draw_entities(entities, player,
                                  game_map, game_camera, cursor_x, cursor_y)
    if len(light_sources) > 0:
        draw_light_sources(player, game_map, game_camera, light_sources)


def draw_light_sources(player, game_map, game_camera, sources):
    light_map = player.player.lightmap
    for light in sources:
        light_fov = np.where(light.fov_map.fov)
        center = np.array([light.owner.y, light.owner.x])

        for i in range(light_fov[0].size):
            y, x = int(light_fov[0][i]), int(light_fov[1][i])
            if player.light_source.fov_map.fov[y, x]:
                v = np.array([y, x])
                dist = float(cityblock(center, v))
                light_level = game_map.tiles[x][y].natural_light_level * \
                              (1.0 / (0.2 + 0.1 * dist + 0.025 * dist * dist))

                if light_map[y][x] < light_level:
                    light_map[y][x] = light_level

    player_fov = np.where(player.light_source.fov_map.fov)
    for j in range(player_fov[0].size):
        y, x = int(player_fov[0][j]), int(player_fov[1][j])
        cam_x, cam_y = game_camera.get_coordinates(x, y)
        blt.layer(0)
        c = blt.color_from_name(game_map.tiles[x][y].color)
        if variables.gfx == "adambolt":
            c = blt.color_from_name("gray")
        argb = argb_from_color(c)
        flicker = random.uniform(0.95, 1.05)
        a = argb[0]
        r = min(int(argb[1] * light_map[y][x] * flicker), 255)
        g = min(int(argb[2] * light_map[y][x] * flicker), 255)
        b = min(int(argb[3] * light_map[y][x] * flicker), 255)

        blt.color(blt.color_from_argb(a, r, g, b))
        blt.put(cam_x * variables.tile_offset_x, cam_y * variables.tile_offset_y,
                game_map.tiles[x][y].char)

        if len(game_map.tiles[x][y].layers) > 0:
            i = 1
            for tile in game_map.tiles[x][y].layers:
                blt.layer(i)
                c = blt.color_from_name(tile[1])
                argb = argb_from_color(c)
                a = argb[0]
                r = min(int(argb[1] * light_map[y][x] * flicker), 255)
                g = min(int(argb[2] * light_map[y][x] * flicker), 255)
                b = min(int(argb[3] * light_map[y][x] * flicker), 255)
                blt.color(blt.color_from_argb(a, r, g, b))
                blt.put(cam_x * variables.tile_offset_x, cam_y * variables.tile_offset_y,
                        tile[0])
                i += 1

        if len(game_map.tiles[x][y].entities_on_tile) > 0:
            for entity in game_map.tiles[x][y].entities_on_tile:

                if not entity.cursor:
                    clear(entity, cam_x, cam_y)
                    draw(entity, game_map, cam_x, cam_y, player)


def draw_messages(msg_panel, message_log):
    if len(variables.stack) > 0 and not variables.stack == variables.old_stack:

        d = dict(Counter(variables.stack))
        formatted_stack = []
        for i in d:
            if d[i] > 1:
                formatted_stack.append(i + " x" + str(d[i]))
            else:
                formatted_stack.append(i)
        message_log.send(
            ". ".join(formatted_stack) + ".")

    if message_log.new_msgs:
        blt.layer(1)
        blt.clear_area(msg_panel.x * variables.ui_offset_x, msg_panel.y * variables.ui_offset_y, msg_panel.w *
                       variables.ui_offset_x, msg_panel.h * variables.ui_offset_y)
        blt.color("white")
        # Print the game messages, one line at a time. Display newest
        # msg at the bottom and scroll others up
        i = 4
        # if i > message_log.max_length:
        #    i = 0
        for msg in message_log.buffer:
            msg = shorten(msg, msg_panel.w * variables.ui_offset_x - 2,
                          placeholder="..(Press 'M' for log)")
            blt.puts(msg_panel.x * variables.ui_offset_x + 1, msg_panel.y *
                     variables.ui_offset_y - 1 + i * 2, "[offset=0,0]" + msg, msg_panel.w * variables.ui_offset_x - 2,
                     1,
                     align=blt.TK_ALIGN_LEFT)
            i -= 1
        message_log.new_msgs = False


def draw_stats(player, target=None):
    power_msg = "Spirit power left: " + str(player.player.spirit_power)
    blt.layer(1)
    blt.clear_area(2, variables.viewport_h + variables.ui_offset_y + 1,
                   int(variables.viewport_w / 2) + int(len(power_msg) / 2 + 5) - 5, 1)
    blt.color("gray")

    # Draw spirit power left and position it depending on window size
    if variables.viewport_w > 90:
        #         blt.puts(int(variables.viewport_w / 2) - int(len(power_msg) / 2) - 5,
        #                  variables.viewport_h + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        #         blt.puts(int(variables.viewport_w / 2) + int(len(power_msg) / 2 + 3),
        #                  variables.viewport_h + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(int(variables.viewport_w / 2),
                 variables.viewport_h + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
                 blt.TK_ALIGN_CENTER)
    else:
        #         blt.puts(variables.viewport_w - len(power_msg) - 5,
        #                  variables.viewport_h + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        #         blt.puts(variables.viewport_w,
        #                  variables.viewport_h + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(variables.viewport_w - len(power_msg),
                 variables.viewport_h + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
                 blt.TK_ALIGN_LEFT)

    # Draw player stats
    if player.fighter.hp / player.fighter.max_hp < 0.34:
        hp_player = "[color=light red]HP:" + \
                    str(player.fighter.hp) + "/" + \
                    str(player.fighter.max_hp) + "  "

    else:
        hp_player = "[color=default]HP:" + \
                    str(player.fighter.hp) + "/" + \
                    str(player.fighter.max_hp) + "  "
    for x in range(len(player.fighter.effects)):
        if player.fighter.effects[x][0] == "poison":
            hp_player = "[color=green]HP:" + \
                        str(player.fighter.hp) + "/" + \
                        str(player.fighter.max_hp) + "  "

    ac_player = "[color=default]AC:" + str(player.fighter.ac) + "  "
    ev_player = "EV:" + str(player.fighter.ev) + "  "
    power_player = "ATK:" + str(player.fighter.power)

    blt.puts(4, variables.viewport_h + variables.ui_offset_y + 1,
             "[offset=0,-2]" + "[color=lightest green]Player:  " + hp_player + ac_player + ev_player + power_player, 0,
             0, blt.TK_ALIGN_LEFT)

    # Draw target stats
    if target:
        blt.clear_area(int(variables.viewport_w / 2) - int(len(power_msg) / 2) - 5,
                       variables.viewport_h + variables.ui_offset_y + 1, variables.viewport_w, 1)
        if target.fighter.hp / target.fighter.max_hp < 0.34:
            hp_target = "[color=light red]HP:" + \
                        str(target.fighter.hp) + "/" + \
                        str(target.fighter.max_hp) + "  "
        else:
            hp_target = "[color=default]HP:" + \
                        str(target.fighter.hp) + "/" + \
                        str(target.fighter.max_hp) + "  "
        ac_target = "[color=default]AC:" + str(target.fighter.ac) + "  "
        ev_target = "EV:" + str(target.fighter.ev) + "  "
        power_target = "ATK:" + str(target.fighter.power) + " "

        blt.puts(variables.viewport_w, variables.viewport_h + variables.ui_offset_y + 1,
                 "[offset=0,-2]" + "[color=lightest red]" + target.name.capitalize() + ":  " + hp_target + ac_target + ev_target + power_target,
                 0, 0, blt.TK_ALIGN_RIGHT)

        if target.fighter.hp <= 0:
            blt.clear_area(2, variables.viewport_h +
                           variables.ui_offset_y + 1, variables.viewport_w, 1)


def draw_ui(ui_elements):
    blt.color("gray")
    blt.layer(0)
    #     for y in range(msg_panel.y, msg_panel.h):
    #         for x in range(msg_panel.x, msg_panel.w):
    #             blt.put_ext(x * variables.ui_offset_x, y *
    #                         variables.ui_offset_y, 0, 0, 0xE100 + 692)

    msg_panel_borders = ui_elements.msg_panel_borders
    screen_borders = ui_elements.screen_borders
    side_panel_borders = ui_elements.side_panel_borders



    for y in range(msg_panel_borders.y, msg_panel_borders.y2):
        for x in range(msg_panel_borders.x, msg_panel_borders.x2):
            if (y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, 10, tilemap_ui()["ui_block_horizontal"])
            elif (y == msg_panel_borders.y2 - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, -10, tilemap_ui()["ui_block_horizontal"])
            elif (x == msg_panel_borders.x):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, 0, tilemap_ui()["ui_block_vertical"])
            elif (x == msg_panel_borders.x2 - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, 0, tilemap_ui()["ui_block_vertical"])
            if (x == msg_panel_borders.x and y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, 10, tilemap_ui()["ui_block_nw"])
            if (x == msg_panel_borders.x2 - 1 and y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, 10, tilemap_ui()["ui_block_ne"])
            if (x == msg_panel_borders.x and y == msg_panel_borders.y2 - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, -10, tilemap_ui()["ui_block_sw"])
            if (x == msg_panel_borders.x2 - 1 and y == msg_panel_borders.y2 - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, -10, tilemap_ui()["ui_block_se"])

    for y in range(screen_borders.y, screen_borders.y2):
        for x in range(screen_borders.x, screen_borders.x2):
            if (y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, tilemap_ui()["ui_block_horizontal"])
            elif (y == screen_borders.y2 - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_horizontal"])
            elif (x == screen_borders.x):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_vertical"])
            elif (x == screen_borders.x2 - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_vertical"])
            if (x == screen_borders.x and y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_nw"])
            if (x == screen_borders.x2 - 1 and y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_ne"])
            if (x == screen_borders.x and y == screen_borders.y2 - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_sw"])
            if (x == screen_borders.x2 - 1 and y == screen_borders.y2 - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_se"])

    for y in range(side_panel_borders.y, side_panel_borders.y2):
        for x in range(side_panel_borders.x, side_panel_borders.x2+1):
            if (y == side_panel_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, tilemap_ui()["ui_block_horizontal"])
            elif (y == side_panel_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_horizontal"])
            elif (x == side_panel_borders.x):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_vertical"])
            elif (x == side_panel_borders.x2):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_vertical"])
            if (x == side_panel_borders.x and y == side_panel_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_nw"])
            if (x == side_panel_borders.x2 and y == side_panel_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_ne"])
            if (x == side_panel_borders.x and y == side_panel_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_sw"])
            if (x == side_panel_borders.x2 and y == side_panel_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_se"])


def draw_indicator(entity_x, entity_y, game_camera, color=None, occupied_tiles=None):
    # Draw player indicator
    blt.layer(4)
    x, y = game_camera.get_coordinates(entity_x, entity_y)
    blt.color(color)
    if occupied_tiles is not None:
        return
    else:
        blt.put_ext(x * variables.tile_offset_x, y *
                    variables.tile_offset_y, 0, 0, tilemap()["indicator"])


def draw_all(game_map, game_camera, player, entities, ui_elements):
    game_camera.move_camera(
        player.x, player.y, game_map.width, game_map.height)
    cursor_x, cursor_y = None, None
    if "cursor" in entities.keys():
        cursor_x = entities["cursor"][0].x
        cursor_y = entities["cursor"][0].y

    draw_map(game_map, game_camera, player, cursor_x, cursor_y)
    draw_ui(ui_elements)
    draw_stats(player)


def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.clear_area(x * variables.tile_offset_x, y *
                   variables.tile_offset_y, 1, 1)
    if entity.boss:
        blt.clear_area(x * variables.tile_offset_x, y *
                       variables.tile_offset_y, 2, 2)


def clear_entities(entities, game_camera):
    for category in entities.values():
        for entity in category:
            x, y = game_camera.get_coordinates(entity.x, entity.y)
            dx, dy = game_camera.get_coordinates(
                entity.last_seen_x, entity.last_seen_y)
            clear(entity, x, y)
            clear(entity, dx, dy)


def clear_camera(n):
    i = 0
    while i < n:
        blt.layer(i)
        blt.clear_area(1, 1, variables.viewport_w, variables.viewport_h)
        i += 1
