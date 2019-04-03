from bearlibterminal import terminal as blt


def draw_entities(entities, game_map, game_camera, fov_map):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        if fov_map.fov[entity.y, entity.x]:
            draw(entity, game_map, x, y)


def draw_map(game_map, game_camera, fov_map, fov_recompute):

    if fov_recompute:
        # Draw all the tiles in the game map
        for y in range(game_camera.height):
            for x in range(game_camera.width):
                map_x, map_y = game_camera.x + x, game_camera.y + y
                visible = fov_map.fov[map_y, map_x]
                wall = game_map.tiles[map_x][map_y].blocked

                if visible:
                    if wall:
                        blt.layer(0)
                        blt.color("darkest amber")
                        blt.put(x, y, 0xE100 + 21)
                        blt.layer(1)
                        blt.color("light orange")
                        if game_map.tiles[map_x][map_y].seed < 50:
                            blt.color("orange")
                        if (0 <= game_map.tiles[map_x][map_y].seed <=
                                int(100 / 6)):
                            blt.put(x, y, 0xE100 + 87)
                        if (int(100 / 6) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 2):
                            blt.put(x, y, 0xE100 + 88)
                        if (int(100 / 6 * 2) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 3):
                            blt.put(x, y, 0xE100 + 89)
                        if (int(100 / 6 * 3) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 4):
                            blt.put(x, y, 0xE100 + 93)
                        if (int(100 / 6 * 4) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 5):
                            blt.put(x, y, 0xE100 + 94)
                        if (int(100 / 6 * 5) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100):
                            blt.put(x, y, 0xE100 + 95)
                    else:
                        blt.color("darkest amber")
                        blt.put(x, y, 0xE100 + 21)
                    game_map.tiles[map_x][map_y].explored = True

                elif game_map.tiles[map_x][map_y].explored:
                    if wall:
                        blt.layer(0)
                        blt.color("darkest gray")
                        blt.put(x, y, 0xE100 + 21)
                        blt.layer(1)
                        blt.color("darkest gray")
                        if (0 <= game_map.tiles[map_x][map_y].seed <=
                                int(100 / 6)):
                            blt.put(x, y, 0xE100 + 87)
                        if (int(100 / 6) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 2):
                            blt.put(x, y, 0xE100 + 88)
                        if (int(100 / 6 * 2) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 3):
                            blt.put(x, y, 0xE100 + 89)
                        if (int(100 / 6 * 3) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 4):
                            blt.put(x, y, 0xE100 + 93)
                        if (int(100 / 6 * 4) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100 / 6 * 5):
                            blt.put(x, y, 0xE100 + 94)
                        if (int(100 / 6 * 5) <=
                            game_map.tiles[map_x][map_y].seed <=
                                100):
                            blt.put(x, y, 0xE100 + 95)
                    else:
                        blt.color("darkest gray")
                        blt.put(x, y, 0xE100 + 21)
                else:
                    blt.layer(0)
                    blt.put(x, y, " ")
                    blt.layer(1)
                    blt.put(x, y, " ")


def draw_all(game_map, game_camera, entities, px, py, fov_map, fov_recompute):

    game_camera.move_camera(
        px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera, fov_map, fov_recompute)
    draw_entities(entities, game_map, game_camera, fov_map)


def clear_entities(entities, game_camera):

    for entity in entities:
        x, y = game_camera.get_coordinates(entity.x, entity.y)
        clear(entity, x, y)


def draw(entity, game_map, x, y):

    # Draw the entity to the screen
    blt.layer(entity.layer)
    blt.color(blt.color_from_name(entity.color))
    blt.put(x, y, entity.char)


def clear(entity, x, y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.put(x, y, " ")
