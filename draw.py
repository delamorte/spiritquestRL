from bearlibterminal import terminal as blt
from math import ceil
from textwrap import shorten
import variables


def draw(entity, game_map, x, y):

    # Draw the entity to the screen
    blt.layer(entity.layer)
    blt.color(blt.color(entity.color))
    if game_map.name is "hub" and entity.player:
        blt.put(x * variables.tile_offset_x, y *
                variables.tile_offset_y, entity.char_hub)
    else:
        blt.put(x * variables.tile_offset_x, y *
                variables.tile_offset_y, entity.char)


def draw_entities(entities, game_map, game_camera, fov_map):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        if fov_map.fov[entity.y, entity.x]:
            draw(entity, game_map, x, y)


def draw_map(game_map, game_camera, fov_map, fov_recompute, viewport_x, viewport_y):

    # Only draw map if player has moved
    if fov_recompute:
        # Clear what's drawn in camera
        clear_camera(viewport_x, viewport_y)
        # Draw all the tiles in the game map
        for y in range(ceil(variables.camera_offset), game_camera.height - ceil(variables.camera_offset)):
            for x in range(ceil(variables.camera_offset), game_camera.width - ceil(variables.camera_offset)):
                map_x, map_y = game_camera.x + x, game_camera.y + y
                visible = fov_map.fov[map_y, map_x]

                # Draw tiles within fov
                if visible:
                    # Draw layer 0 + 1 first
                    if not game_map.tiles[map_x][map_y].char == " ":
                        blt.layer(0)
                        blt.color("darkest amber")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char_ground)
                        blt.layer(1)
                        blt.color(game_map.tiles[map_x][map_y].color)
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char)
                    # Fill rest of fov with ground tiles
                    else:
                        blt.color("darkest amber")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char_ground)
                    # Set everything in fov as explored
                    game_map.tiles[map_x][map_y].explored = True

                # Gray out explored tiles
                elif game_map.tiles[map_x][map_y].explored:
                    if not game_map.tiles[map_x][map_y].char == " ":
                        blt.layer(0)
                        blt.color("darkest gray")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char_ground)
                        blt.layer(1)
                        blt.color("darkest gray")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char)
                    else:
                        blt.color("darkest gray")
                        blt.put(x * variables.tile_offset_x, y * variables.tile_offset_y,
                                game_map.tiles[map_x][map_y].char_ground)


def draw_messages(msg_panel, message_log, player, power_msg, viewport_x, viewport_y):

    if message_log.update:
        blt.layer(1)
        blt.clear_area(msg_panel.x * variables.ui_offset_x, msg_panel.y * variables.ui_offset_y, msg_panel.w *
                       variables.ui_offset_x, msg_panel.h * variables.ui_offset_y)
        blt.color("white")
        # Print the game messages, one line at a time. Display newest
        # msg at the bottom and scroll others up
        i = 5
        #if i > message_log.max_length:
        #    i = 0
        for msg in message_log.buffer:
            msg = shorten(msg, msg_panel.w * variables.ui_offset_x - 2,
                          placeholder="..(Press 'M' for log)")
            blt.puts(msg_panel.x * variables.ui_offset_x + 1, msg_panel.y *
                     variables.ui_offset_y + i, "[offset=0,-9]" + msg, msg_panel.w * variables.ui_offset_x - 2, 1, align=blt.TK_ALIGN_LEFT)
            i -= 1
        message_log.update(message_log.buffer)

def draw_stats(player, viewport_x, viewport_y, power_msg, target=None):

    blt.layer(8)
    blt.clear_area(2, viewport_y + variables.ui_offset_y + 1, int(viewport_x / 2) + int(len(power_msg) / 2 + 5) - 5, 1)
    blt.color("gray")

    #Draw spirit power left and position it depending on window size
    if viewport_x > 90:
        blt.puts(int(viewport_x / 2) - int(len(power_msg) / 2) - 5,
                 viewport_y + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.puts(int(viewport_x / 2) + int(len(power_msg) / 2 + 3),
                 viewport_y + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(int(viewport_x / 2),
                 viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0, blt.TK_ALIGN_CENTER)
    else:
        blt.puts(viewport_x - len(power_msg) - 5,
                 viewport_y + variables.ui_offset_y, "[offset=0,5]" + "[U+EAB8]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.puts(viewport_x,
                 viewport_y + variables.ui_offset_y, "[offset=0,2]" + "[U+EADC]", 0, 0, blt.TK_ALIGN_CENTER)
        blt.color("default")
        blt.puts(viewport_x - len(power_msg),
                 viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + power_msg, 0, 0, blt.TK_ALIGN_LEFT)

    # Draw player stats
    if player.fighter_c.hp / player.fighter_c.max_hp < 0.34:
        hp_player = "[color=light red]HP:" + str(player.fighter_c.hp) + "/" + str(player.fighter_c.max_hp) + "  "
    else:
        hp_player = "[color=default]HP:" + str(player.fighter_c.hp) + "/" + str(player.fighter_c.max_hp) + "  "
    
    ac_player = "[color=default]AC:" + str(player.fighter_c.ac) + "  "
    ev_player = "EV:" + str(player.fighter_c.ev) + "  "
    power_player = "ATK:" + str(player.fighter_c.power)
    
    blt.puts(4, viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + "[color=lightest green]Player:  " + hp_player + ac_player + ev_player + power_player, 0, 0, blt.TK_ALIGN_LEFT)
    
    # Draw target stats
    if target:
        blt.clear_area(int(viewport_x / 2) - int(len(power_msg) / 2) - 5, viewport_y + variables.ui_offset_y + 1, viewport_x, 1)
        if target.fighter_c.hp / target.fighter_c.max_hp < 0.34:
            hp_target = "[color=light red]HP:" + str(target.fighter_c.hp) + "/" + str(target.fighter_c.max_hp) + "  "
        else:
            hp_target = "[color=default]HP:" + str(target.fighter_c.hp) + "/" + str(target.fighter_c.max_hp) + "  "
        ac_target = "[color=default]AC:" + str(target.fighter_c.ac) + "  "
        ev_target = "EV:" + str(target.fighter_c.ev) + "  "
        power_target = "ATK:" + str(target.fighter_c.power) + " "
    
        blt.puts(viewport_x, viewport_y + variables.ui_offset_y + 1, "[offset=0,-2]" + "[color=lightest red]Enemy:  " + hp_target + ac_target + ev_target + power_target, 0, 0, blt.TK_ALIGN_RIGHT)
        
        if target.fighter_c.hp <= 0:
            blt.clear_area(2, viewport_y + variables.ui_offset_y + 1, viewport_x, 1)


def draw_ui(viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders):
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
             fov_recompute, message_log, msg_panel, power_msg,
             viewport_x, viewport_y):

    game_camera.move_camera(
        px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera, fov_map,
             fov_recompute, viewport_x, viewport_y)
    draw_entities(entities, game_map, game_camera, fov_map)
    draw_messages(msg_panel, message_log, player,
                  power_msg, viewport_x, viewport_y)
    draw_stats(player, viewport_x, viewport_y, power_msg)

def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.clear_area(x * variables.tile_offset_x, y * variables.tile_offset_y, 1, 1)


def clear_entities(entities, game_camera):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        clear(entity, x, y)


def clear_camera(viewport_x, viewport_y):
    i = 0
    while i < 10:
        blt.layer(i)
        blt.clear_area(1, 1, viewport_x, viewport_y)
        i += 1
