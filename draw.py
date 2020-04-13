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


def draw(entity, game_map, x, y, fov_map):
    # if variables.gfx == "adambolt" and entity.fighter:
    #     blt.layer(0)
    #     blt.color("lighter amber")
    #     blt.put(x * variables.tile_offset_x, y *
    #             variables.tile_offset_y, 0xE700 + 3)

    # Draw the entity to the screen
    blt.layer(entity.layer)

    c = blt.color_from_name(entity.color)
    if variables.gfx == "adambolt":
        c = blt.color_from_name(None)
    argb = argb_from_color(c)
    r = int(argb[1] * game_map.tiles[entity.x][entity.y].light_level)
    g = int(argb[2] * game_map.tiles[entity.x][entity.y].light_level)
    b = int(argb[3] * game_map.tiles[entity.x][entity.y].light_level)
    blt.color(blt.color_from_argb(255, r, g, b))


    # if variables.gfx == "adambolt":
    #     blt.color(None)

    if not (fov_map.fov[entity.y, entity.x] and
            game_map.tiles[entity.x][entity.y].explored):
        blt.color("gray")

    # Cursor needs some offset in ascii
    if variables.gfx == "ascii" and entity.name == "cursor":
        blt.put_ext(x * variables.tile_offset_x, y *
                    variables.tile_offset_y, -3 * variables.tile_offset_x, -5 * variables.tile_offset_y, entity.char)
    else:
        blt.put(x * variables.tile_offset_x, y *
                variables.tile_offset_y, entity.char)


def draw_entities(entities, player, game_map, game_camera, fov_map, cursor_x, cursor_y):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)

        if entity.x == player.x and entity.y == player.y and entity.stand_on_messages:

            variables.stack.append(get_article(
                entity.name).capitalize() + " " + entity.name)
            if entity.xtra_info:
                variables.stack.append(entity.xtra_info)

        if cursor_x is not None:
            if (entity.x == cursor_x and entity.y == cursor_y and not
                    entity.cursor and game_map.tiles[entity.x][entity.y].explored):

                variables.stack.append(get_article(entity.name).capitalize() + " " + entity.name)
                variables.stack.append(str("x: " + (str(cursor_x) + ", y: " + str(cursor_y))))

                if entity.xtra_info:
                    variables.stack.append(entity.xtra_info)

                if entity.fighter:
                    draw_stats(player, entity)

            if entity.name == "cursor":
                clear(entity, entity.last_seen_x, entity.last_seen_y)
                draw(entity, game_map, x, y, fov_map)

        if not entity.cursor and fov_map.fov[entity.y, entity.x]:
            # why is this here? causes rendering bugs!!!
            # clear(entity, entity.last_seen_x, entity.last_seen_y)

            if not entity.player and not entity.cursor:
                entity.last_seen_x = entity.x
                entity.last_seen_y = entity.y

            draw(entity, game_map, x, y, fov_map)

        elif (not fov_map.fov[entity.y, entity.x] and
              game_map.tiles[entity.last_seen_x][entity.last_seen_y].explored and not
              fov_map.fov[entity.last_seen_y, entity.last_seen_x]):

            x, y = game_camera.get_coordinates(entity.last_seen_x, entity.last_seen_y)

            # what is this if???????
            # if (ceil(variables.camera_offset) < x < game_camera.width - ceil(variables.camera_offset) and ceil(
            #        variables.camera_offset) < y < game_camera.height - ceil(variables.camera_offset)):
            draw(entity, game_map, x, y, fov_map)

        if fov_map.fov[entity.y, entity.x] and entity.ai and variables.gfx != "ascii":
            draw_indicator(player.x, player.y, game_camera, "gray")
            draw_indicator(entity.x, entity.y, game_camera, "dark red")


def draw_map(game_map, game_camera, fov_map, player, cursor_x, cursor_y):
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
            visible = fov_map.fov[map_y, map_x]

            # Draw tiles within fov
            if visible:
                blt.layer(0)
                dist = float(cityblock(center, np.array([map_y, map_x])))
                game_map.tiles[map_x][map_y].light_level = (1.0 / (1.05 + 0.035 * dist + 0.025 * dist * dist))

                c = blt.color_from_name(game_map.tiles[map_x][map_y].color)
                if variables.gfx == "adambolt":
                    c = blt.color_from_name("gray")
                argb = argb_from_color(c)
                r = int(argb[1] * game_map.tiles[map_x][map_y].light_level)
                g = int(argb[2] * game_map.tiles[map_x][map_y].light_level)
                b = int(argb[3] * game_map.tiles[map_x][map_y].light_level)
                blt.color(blt.color_from_argb(255, r, g, b))

                # elif variables.gfx == "ascii":
                #     blt.color("#CCDDDDDD")
                blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                        game_map.tiles[map_x][map_y].char)
                if len(game_map.tiles[map_x][map_y].layers) > 0:
                    i = 1
                    for tile in game_map.tiles[map_x][map_y].layers:
                        blt.layer(i)
                        blt.color(tile[1])
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
                entities.extend(game_map.tiles[map_x][map_y].entities_on_tile)

    draw_entities(entities, player,
                  game_map, game_camera, fov_map, cursor_x, cursor_y)

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
    blt.clear_area(2, variables.viewport_y + variables.ui_offset_y + 1,
                   int(variables.viewport_x / 2) + int(len(power_msg) / 2 + 5) - 5, 1)
    blt.color("gray")

    # Draw spirit power left and position it depending on window size
    if variables.viewport_x > 90:
        #         blt.puts(int(variables.viewport_x / 2) - int(len(power_msg) / 2) - 5,
        #                  variables.viewport_y + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        #         blt.puts(int(variables.viewport_x / 2) + int(len(power_msg) / 2 + 3),
        #                  variables.viewport_y + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(int(variables.viewport_x / 2),
                 variables.viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
                 blt.TK_ALIGN_CENTER)
    else:
        #         blt.puts(variables.viewport_x - len(power_msg) - 5,
        #                  variables.viewport_y + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        #         blt.puts(variables.viewport_x,
        #                  variables.viewport_y + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(variables.viewport_x - len(power_msg),
                 variables.viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0,
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

    blt.puts(4, variables.viewport_y + variables.ui_offset_y + 1,
             "[offset=0,-2]" + "[color=lightest green]Player:  " + hp_player + ac_player + ev_player + power_player, 0,
             0, blt.TK_ALIGN_LEFT)

    # Draw target stats
    if target:
        blt.clear_area(int(variables.viewport_x / 2) - int(len(power_msg) / 2) - 5,
                       variables.viewport_y + variables.ui_offset_y + 1, variables.viewport_x, 1)
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

        blt.puts(variables.viewport_x, variables.viewport_y + variables.ui_offset_y + 1,
                 "[offset=0,-2]" + "[color=lightest red]" + target.name.capitalize() + ":  " + hp_target + ac_target + ev_target + power_target,
                 0, 0, blt.TK_ALIGN_RIGHT)

        if target.fighter.hp <= 0:
            blt.clear_area(2, variables.viewport_y +
                           variables.ui_offset_y + 1, variables.viewport_x, 1)


def draw_ui(msg_panel, msg_panel_borders, screen_borders):
    blt.color("gray")
    blt.layer(0)
    #     for y in range(msg_panel.y, msg_panel.h):
    #         for x in range(msg_panel.x, msg_panel.w):
    #             blt.put_ext(x * variables.ui_offset_x, y *
    #                         variables.ui_offset_y, 0, 0, 0xE100 + 692)

    for y in range(msg_panel_borders.y, msg_panel_borders.h):
        for x in range(msg_panel_borders.x, msg_panel_borders.w):
            if (y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, 10, tilemap_ui()["ui_block_horizontal"])
            elif (y == msg_panel_borders.h - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, -10, tilemap_ui()["ui_block_horizontal"])
            elif (x == msg_panel_borders.x):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, 0, tilemap_ui()["ui_block_vertical"])
            elif (x == msg_panel_borders.w - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, 0, tilemap_ui()["ui_block_vertical"])
            if (x == msg_panel_borders.x and y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, 10, tilemap_ui()["ui_block_nw"])
            if (x == msg_panel_borders.w - 1 and y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, 10, tilemap_ui()["ui_block_ne"])
            if (x == msg_panel_borders.x and y == msg_panel_borders.h - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, -10, tilemap_ui()["ui_block_sw"])
            if (x == msg_panel_borders.w - 1 and y == msg_panel_borders.h - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, -10, tilemap_ui()["ui_block_se"])

    for y in range(screen_borders.y, screen_borders.h):
        for x in range(screen_borders.x, screen_borders.w):
            if (y == screen_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, 0, tilemap_ui()["ui_block_horizontal"])
            elif (y == screen_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_horizontal"])
            elif (x == screen_borders.x):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_vertical"])
            elif (x == screen_borders.w - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_vertical"])
            if (x == screen_borders.x and y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_nw"])
            if (x == screen_borders.w - 1 and y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_ne"])
            if (x == screen_borders.x and y == screen_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_sw"])
            if (x == screen_borders.w - 1 and y == screen_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, tilemap_ui()["ui_block_se"])


def draw_indicator(entity_x, entity_y, game_camera, color=None):
    # Draw player indicator
    blt.layer(4)
    x, y = game_camera.get_coordinates(entity_x, entity_y)
    blt.color(color)
    blt.put_ext(x * variables.tile_offset_x, y *
                variables.tile_offset_y, 0, 0, tilemap()["indicator"])



def draw_all(game_map, game_camera, player, entities, fov_map, msg_panel, msg_panel_borders, screen_borders):
    game_camera.move_camera(
        player.x, player.y, game_map.width, game_map.height)
    cursor_x, cursor_y = None, None
    if "cursor" in entities.keys():
        cursor_x = entities["cursor"][0].x
        cursor_y = entities["cursor"][0].y

    draw_map(game_map, game_camera, fov_map, player, cursor_x, cursor_y)
    draw_ui(msg_panel, msg_panel_borders, screen_borders)
    draw_stats(player)


def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.clear_area(x * variables.tile_offset_x, y *
                   variables.tile_offset_y, 1, 1)


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
        blt.clear_area(1, 1, variables.viewport_x, variables.viewport_y)
        i += 1
