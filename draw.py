from bearlibterminal import terminal as blt


def draw(entity, game_map, x, y):

    # Draw the entity to the screen
    blt.layer(entity.layer)
    blt.color(blt.color_from_name(entity.color))
    blt.put(x * 4, y * 2, entity.char)


def draw_entities(entities, game_map, game_camera, fov_map):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        if fov_map.fov[entity.y, entity.x]:
            draw(entity, game_map, x, y)


def draw_map(game_map, game_camera, fov_map, fov_recompute):

    # Only draw map if player has moved
    if fov_recompute:
        # Clear what's drawn in camera
        clear_camera(game_camera)
        # Draw all the tiles in the game map
        for y in range(1, game_camera.height-1):
            for x in range(1, game_camera.width-1):
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


def draw_messages(msg_panel, message_log):

    blt.layer(2)
    blt.clear_area(msg_panel.x * 4, msg_panel.y * 2, msg_panel.w *
                   4, msg_panel.h * 2)
    blt.color("white")
    # Print the game messages, one line at a time. Display newest
    # msg at the top and scroll others down
    i = 0
    if i > message_log.max_length:
        i = 0
    for msg in message_log.buffer:
        blt.printf(msg_panel.x * 4 + 1, msg_panel.y * 2 + i, msg)
        i += 1

    message_log.update(message_log.buffer)


def draw_ui(msg_panel):
    blt.layer(0)
    blt.color("darkest gray")
    for y in range(msg_panel.y, msg_panel.h):
        for x in range(msg_panel.x, msg_panel.w):
            blt.put(x * 4, y * 2, 0xE100 + 5)


def draw_all(game_map, game_camera, entities, px, py, fov_map,
             fov_recompute, message_log, msg_panel):

    game_camera.move_camera(
        px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera, fov_map, fov_recompute)
    draw_entities(entities, game_map, game_camera, fov_map)
    if message_log.update:
        draw_messages(msg_panel, message_log)


def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.put(x * 4, y * 2, " ")


def clear_entities(entities, game_camera):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        clear(entity, x, y)


def clear_camera(game_camera):
    blt.layer(0)
    blt.clear_area(0, 0, game_camera.width * 4, game_camera.height * 2)
    blt.layer(1)
    blt.clear_area(0, 0, game_camera.width * 4, game_camera.height * 2)
    blt.layer(2)
    blt.clear_area(0, 0, game_camera.width * 4, game_camera.height * 2)
