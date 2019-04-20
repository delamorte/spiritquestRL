from bearlibterminal import terminal as blt
from textwrap import shorten


def draw(entity, game_map, x, y):

    # Draw the entity to the screen
    blt.layer(entity.layer)
    blt.color(blt.color(entity.color))
    if game_map.name is "hub" and entity.player:
        blt.put(x * 4, y * 2, entity.char_hub)
    else:
        blt.put(x * 4, y * 2, entity.char)


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
        for y in range(1, game_camera.height - 1):
            for x in range(1, game_camera.width - 1):
                map_x, map_y = game_camera.x + x, game_camera.y + y
                visible = fov_map.fov[map_y, map_x]

                # Draw tiles within fov
                if visible:
                    # Draw layer 0 + 1 first
                    if not game_map.tiles[map_x][map_y].char == " ":
                        blt.layer(0)
                        blt.color("darkest amber")
                        blt.put(x * 4, y * 2,
                                game_map.tiles[map_x][map_y].char_ground)
                        blt.layer(1)
                        blt.color(game_map.tiles[map_x][map_y].color)
                        blt.put(x * 4, y * 2,
                                game_map.tiles[map_x][map_y].char)
                    # Fill rest of fov with ground tiles
                    else:
                        blt.color("darkest amber")
                        blt.put(x * 4, y * 2,
                                game_map.tiles[map_x][map_y].char_ground)
                    # Set everything in fov as explored
                    game_map.tiles[map_x][map_y].explored = True

                # Gray out explored tiles
                elif game_map.tiles[map_x][map_y].explored:
                    if not game_map.tiles[map_x][map_y].char == " ":
                        blt.layer(0)
                        blt.color("darkest gray")
                        blt.put(x * 4, y * 2,
                                game_map.tiles[map_x][map_y].char_ground)
                        blt.layer(1)
                        blt.color("darkest gray")
                        blt.put(x * 4, y * 2,
                                game_map.tiles[map_x][map_y].char)
                    else:
                        blt.color("darkest gray")
                        blt.put(x * 4, y * 2,
                                game_map.tiles[map_x][map_y].char_ground)


def draw_messages(msg_panel, message_log, player, power_msg, viewport_x, viewport_y):

    blt.layer(8)
    blt.color("default")
    blt.clear_area(2, viewport_y + 3, viewport_x, 1)
    blt.printf(int(viewport_x / 2 - len(power_msg) / 2),
               viewport_y + 3, "[offset=0,-2, align=middle]" + power_msg)


    hp = "HP:" + str(player.fighter_c.hp) + "/" + str(player.fighter_c.max_hp)
    ac = "AC:" + str(player.fighter_c.ac)
    ev = "EV:" + str(player.fighter_c.ev)
    power = "ATK:" + str(player.fighter_c.power)

    if player.fighter_c.hp / player.fighter_c.max_hp < 0.34:
        blt.color("light red")

    blt.puts(3, viewport_y + 3, "[offset=0,-2]" + hp)
    blt.color("default")
    blt.puts(5+len(hp), viewport_y + 3, "[offset=0,-2]" + ac)
    blt.puts(7+len(hp)+len(ac), viewport_y + 3, "[offset=0,-2]" + ev)
    blt.puts(9+len(hp)+len(ac)+len(ev), viewport_y + 3, "[offset=0,-2]" + power)

    if message_log.update:
        blt.layer(1)
        blt.clear_area(msg_panel.x * 4, msg_panel.y * 2, msg_panel.w *
                       4, msg_panel.h * 2)
        blt.color("white")
        # Print the game messages, one line at a time. Display newest
        # msg at the top and scroll others down
        i = 0
        if i > message_log.max_length:
            i = 0
        for msg in message_log.buffer:
            msg = shorten(msg, msg_panel.w * 4 - 2,
                          placeholder="..(Press 'M' for log)")
            blt.puts(msg_panel.x * 4 + 1, msg_panel.y *
                     2 + i, "[offset=0,9]" + msg, msg_panel.w * 4 - 2, 1, align=blt.TK_ALIGN_LEFT)
            i += 1
        message_log.update(message_log.buffer)


def draw_ui(viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders):
    blt.layer(0)
    blt.color("dark gray")
    for y in range(msg_panel.y, msg_panel.h):
        for x in range(msg_panel.x, msg_panel.w):
            blt.put_ext(x * 4, y * 2, 0, 0, 0xE100 + 19)

    for y in range(msg_panel_borders.y, msg_panel_borders.h):
        for x in range(msg_panel_borders.x, msg_panel_borders.w):
            if (y == msg_panel_borders.y):
                blt.put_ext(x * 4, y * 2, 0, 10, 0xE100 + 472)
            elif (y == msg_panel_borders.h - 1):
                blt.put_ext(x * 4, y * 2, 0, -10, 0xE100 + 441)
            elif(x == msg_panel_borders.x):
                blt.put_ext(x * 4, y * 2, 10, 0, 0xE100 + 440)
            elif(x == msg_panel_borders.w - 1):
                blt.put_ext(x * 4, y * 2, -10, 0, 0xE100 + 476)
            if(x == msg_panel_borders.x and y == msg_panel_borders.y):
                blt.put_ext(x * 4, y * 2, 10, 10, 0xE100 + 468)
            if(x == msg_panel_borders.w - 1 and y == msg_panel_borders.y):
                blt.put_ext(x * 4, y * 2, -10, 10, 0xE100 + 468)
            if(x == msg_panel_borders.x and y == msg_panel_borders.h - 1):
                blt.put_ext(x * 4, y * 2, 10, -10, 0xE100 + 468)
            if(x == msg_panel_borders.w - 1 and y == msg_panel_borders.h - 1):
                blt.put_ext(x * 4, y * 2, -10, -10, 0xE100 + 468)

    blt.layer(8)
    blt.color("gray")
    for y in range(screen_borders.y, screen_borders.h):
        for x in range(screen_borders.x, screen_borders.w):
            if (y == screen_borders.y):
                blt.put_ext(x * 4, y * 2, 0, 0, 0xE100 + 472)
            elif (y == screen_borders.h - 1):
                blt.put(x * 4, y * 2, 0xE100 + 441)
            elif(x == screen_borders.x):
                blt.put(x * 4, y * 2, 0xE100 + 440)
            elif(x == screen_borders.w - 1):
                blt.put(x * 4, y * 2, 0xE100 + 476)
            if(x == screen_borders.x and y == screen_borders.y):
                blt.put(x * 4, y * 2, 0xE100 + 468)
            if(x == screen_borders.w - 1 and y == screen_borders.y):
                blt.put(x * 4, y * 2, 0xE100 + 468)
            if(x == screen_borders.x and y == screen_borders.h - 1):
                blt.put(x * 4, y * 2, 0xE100 + 468)
            if(x == screen_borders.w - 1 and y == screen_borders.h - 1):
                blt.put(x * 4, y * 2, 0xE100 + 468)

    blt.put_ext(int(viewport_x / 2) - 15, y * 2 + 1, 0, 5, 0xE100 + 440)
    blt.put_ext(int(viewport_x / 2) + 12, y * 2 + 1, 0, 5, 0xE100 + 476)


def draw_all(game_map, game_camera, entities, player, px, py, fov_map,
             fov_recompute, message_log, msg_panel, power_msg,
             viewport_x, viewport_y):

    game_camera.move_camera(
        px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera, fov_map,
             fov_recompute, viewport_x, viewport_y)
    draw_entities(entities, game_map, game_camera, fov_map)
    draw_messages(msg_panel, message_log, player, power_msg, viewport_x, viewport_y)


def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.clear_area(x * 4, y * 2, 1, 1)


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
