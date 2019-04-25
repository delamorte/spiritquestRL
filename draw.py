from bearlibterminal import terminal as blt
from math import ceil
from textwrap import shorten
import variables


def draw(entity, game_map, x, y, fov_map):

    # Draw the entity to the screen
    blt.layer(entity.layer)
    blt.color(entity.color)
    if not (fov_map.fov[entity.y, entity.x] and
    game_map.tiles[entity.x][entity.y].explored):
        blt.color("gray")

    blt.put(x * variables.tile_offset_x, y *
            variables.tile_offset_y, entity.char)

    # Draw player indicator
    #
    # if entity.player:
    #     blt.layer(9)
    #     blt.color("#FF3E6643")
    #     blt.put_ext(x * variables.tile_offset_x, y *
    #             variables.tile_offset_y, 12, -12, 0xE100 + 1743)


def draw_entities(entities, game_map, game_camera, fov_map):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        if fov_map.fov[entity.y, entity.x]:
            clear(entity, entity.last_seen_x, entity.last_seen_y)
            entity.last_seen_x = entity.x
            entity.last_seen_y = entity.y
            draw(entity, game_map, x, y, fov_map)

        elif not fov_map.fov[entity.y, entity.x] and game_map.tiles[entity.x][entity.y].explored:
            x, y = game_camera.get_coordinates(
                entity.last_seen_x, entity.last_seen_y)
            if (x > ceil(variables.camera_offset) and y > ceil(variables.camera_offset) and
                x < game_camera.width - ceil(variables.camera_offset) and
                    y < game_camera.height - ceil(variables.camera_offset)):
                draw(entity, game_map, x, y, fov_map)


def draw_map(game_map, game_camera, fov_map, fov_recompute):

    # Only draw map if player has moved
    if fov_recompute:
        # Clear what's drawn in camera
        clear_camera()
        # Draw all the tiles in the game map
        for y in range(ceil(variables.camera_offset), game_camera.height - ceil(variables.camera_offset)):
            for x in range(ceil(variables.camera_offset), game_camera.width - ceil(variables.camera_offset)):
                map_x, map_y = game_camera.x + x, game_camera.y + y
                visible = fov_map.fov[map_y, map_x]
                
                # Draw tiles within fov
                if visible:
                    # Draw layers in order
                    if not game_map.tiles[map_x][map_y].char[1] == " ":
                        blt.layer(0)
                        blt.color(game_map.tiles[map_x][map_y].color[0])
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char[0])

                        blt.layer(1)
                        blt.color(game_map.tiles[map_x][map_y].color[1])
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char[1])
                    # Fill rest of fov with ground tiles
                    else:
                        blt.color(game_map.tiles[map_x][map_y].color[0])
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char[0])
                    # Set everything in fov as explored
                    game_map.tiles[map_x][map_y].explored = True

                # Gray out explored tiles
                elif game_map.tiles[map_x][map_y].explored:
                    if not game_map.tiles[map_x][map_y].char[1] == " ":
                        blt.layer(0)
                        blt.color("darkest gray")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char[0])

                        blt.layer(1)
                        blt.color("darkest gray")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char[1])
                    else:
                        blt.color("darkest gray")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char[0])


def draw_messages(msg_panel, message_log):

    if message_log.update:
        blt.layer(1)
        blt.clear_area(msg_panel.x * variables.ui_offset_x, msg_panel.y * variables.ui_offset_y, msg_panel.w *
                       variables.ui_offset_x, msg_panel.h * variables.ui_offset_y)
        blt.color("white")
        # Print the game messages, one line at a time. Display newest
        # msg at the bottom and scroll others up
        i = 5
        # if i > message_log.max_length:
        #    i = 0
        for msg in message_log.buffer:
            msg = shorten(msg, msg_panel.w * variables.ui_offset_x - 2,
                          placeholder="..(Press 'M' for log)")
            blt.puts(msg_panel.x * variables.ui_offset_x + 1, msg_panel.y *
                     variables.ui_offset_y + i, "[offset=0,-9]" + msg, msg_panel.w * variables.ui_offset_x - 2, 1, align=blt.TK_ALIGN_LEFT)
            i -= 1
        message_log.update(message_log.buffer)


def draw_stats(player, target=None):

    power_msg = "Spirit power left: " + str(player.player.spirit_power)
    blt.layer(8)
    blt.clear_area(2, variables.viewport_y + variables.ui_offset_y + 1,
                   int(variables.viewport_x / 2) + int(len(power_msg) / 2 + 5) - 5, 1)
    blt.color("gray")

    # Draw spirit power left and position it depending on window size
    if variables.viewport_x > 90:
        blt.puts(int(variables.viewport_x / 2) - int(len(power_msg) / 2) - 5,
                 variables.viewport_y + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.puts(int(variables.viewport_x / 2) + int(len(power_msg) / 2 + 3),
                 variables.viewport_y + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(int(variables.viewport_x / 2),
                 variables.viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0, blt.TK_ALIGN_CENTER)
    else:
        blt.puts(variables.viewport_x - len(power_msg) - 5,
                 variables.viewport_y + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.puts(variables.viewport_x,
                 variables.viewport_y + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(variables.viewport_x - len(power_msg),
                 variables.viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0, blt.TK_ALIGN_LEFT)

    # Draw player stats
    if player.fighter.hp / player.fighter.max_hp < 0.34:
        hp_player = "[color=light red]HP:" + \
            str(player.fighter.hp) + "/" + \
            str(player.fighter.max_hp) + "  "
    else:
        hp_player = "[color=default]HP:" + \
            str(player.fighter.hp) + "/" + \
            str(player.fighter.max_hp) + "  "

    ac_player = "[color=default]AC:" + str(player.fighter.ac) + "  "
    ev_player = "EV:" + str(player.fighter.ev) + "  "
    power_player = "ATK:" + str(player.fighter.power)

    blt.puts(4, variables.viewport_y + variables.ui_offset_y + 1,
             "[offset=0,-2]" + "[color=lightest green]Player:  " + hp_player + ac_player + ev_player + power_player, 0, 0, blt.TK_ALIGN_LEFT)

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
                 "[offset=0,-2]" + "[color=lightest red]Enemy:  " + hp_target + ac_target + ev_target + power_target, 0, 0, blt.TK_ALIGN_RIGHT)

        if target.fighter.hp <= 0:
            blt.clear_area(2, variables.viewport_y +
                           variables.ui_offset_y + 1, variables.viewport_x, 1)


def draw_ui(msg_panel, msg_panel_borders, screen_borders):
    blt.layer(0)
    blt.color("dark gray")

    for y in range(msg_panel.y, msg_panel.h):
        for x in range(msg_panel.x, msg_panel.w):
            blt.put_ext(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0, 0, 0xE900 + 19)

    for y in range(msg_panel_borders.y, msg_panel_borders.h):
        for x in range(msg_panel_borders.x, msg_panel_borders.w):
            if (y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, 10, 0xE900 + 472)
            elif (y == msg_panel_borders.h - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, -10, 0xE900 + 441)
            elif(x == msg_panel_borders.x):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, 0, 0xE900 + 440)
            elif(x == msg_panel_borders.w - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, 0, 0xE900 + 476)
            if(x == msg_panel_borders.x and y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, 10, 0xE900 + 468)
            if(x == msg_panel_borders.w - 1 and y == msg_panel_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, 10, 0xE900 + 468)
            if(x == msg_panel_borders.x and y == msg_panel_borders.h - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 10, -10, 0xE900 + 468)
            if(x == msg_panel_borders.w - 1 and y == msg_panel_borders.h - 1):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, -10, -10, 0xE900 + 468)

    blt.layer(8)
    blt.color("gray")
    for y in range(screen_borders.y, screen_borders.h):
        for x in range(screen_borders.x, screen_borders.w):
            if (y == screen_borders.y):
                blt.put_ext(x * variables.ui_offset_x, y *
                            variables.ui_offset_y, 0, 0, 0xE900 + 472)
            elif (y == screen_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 441)
            elif(x == screen_borders.x):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 440)
            elif(x == screen_borders.w - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 476)
            if(x == screen_borders.x and y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 468)
            if(x == screen_borders.w - 1 and y == screen_borders.y):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 468)
            if(x == screen_borders.x and y == screen_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 468)
            if(x == screen_borders.w - 1 and y == screen_borders.h - 1):
                blt.put(x * variables.ui_offset_x, y *
                        variables.ui_offset_y, 0xE900 + 468)


def draw_all(game_map, game_camera, entities, player, px, py, fov_map,
             fov_recompute, message_log, msg_panel):

    game_camera.move_camera(
        px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera, fov_map,
             fov_recompute)
    draw_entities(entities, game_map, game_camera, fov_map)
    draw_messages(msg_panel, message_log)
    draw_stats(player)


def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.clear_area(x * variables.tile_offset_x, y *
                   variables.tile_offset_y, 1, 1)


def clear_entities(entities, game_camera):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        dx, dy = game_camera.get_coordinates(
            entity.last_seen_x, entity.last_seen_y)
        clear(entity, x, y)
        clear(entity, dx, dy)


def clear_camera():
    i = 0
    while i < 10:
        blt.layer(i)
        blt.clear_area(1, 1, variables.viewport_x, variables.viewport_y)
        i += 1
