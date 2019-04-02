from bearlibterminal import terminal as blt
from tcod import map_is_in_fov


def draw_entities(entities, game_map, game_camera):

    for entity in entities:
        #camera_x, camera_y = game_camera.get_coordinates(entity.x, entity.y)
        draw(entity, game_map, entity.x, entity.y)


def draw_map(game_map, game_camera, fov_map, fov_recompute):

    for y in range(game_map.height):
        for x in range(game_map.width):
            blt.put(x, y, " ")

    if fov_recompute:
        # Draw all the tiles in the game map
        for y in range(game_map.height):
            for x in range(game_map.width):
                #map_x, map_y = game_camera.x + x, game_camera.y + y
                visible = fov_map.fov[y, x]
                #wall = game_map.tiles[x][y].block_sight

                if visible:
                    if game_map.tiles[x][y].forest:
                        blt.layer(0)
                        blt.color("darkest amber")
                        blt.put(x, y, 0xE100 + 21)
                        blt.layer(1)
                        blt.color("light orange")
                        if game_map.tiles[x][y].seed < 50:
                            blt.color("orange")
                        if 0 <= game_map.tiles[x][y].seed <= int(100 / 6):
                            blt.put(x, y, 0xE100 + 87)
                        if int(100 / 6) <= game_map.tiles[x][y].seed <= 100 / 6 * 2:
                            blt.put(x, y, 0xE100 + 88)
                        if int(100 / 6 * 2) <= game_map.tiles[x][y].seed <= 100 / 6 * 3:
                            blt.put(x, y, 0xE100 + 89)
                        if int(100 / 6 * 3) <= game_map.tiles[x][y].seed <= 100 / 6 * 4:
                            blt.put(x, y, 0xE100 + 93)
                        if int(100 / 6 * 4) <= game_map.tiles[x][y].seed <= 100 / 6 * 5:
                            blt.put(x, y, 0xE100 + 94)
                        if int(100 / 6 * 5) <= game_map.tiles[x][y].seed <= 100:
                            blt.put(x, y, 0xE100 + 95)
                    else:
                        # Draw floor tiles
                        blt.color("darkest amber")
                        blt.put(x, y, 0xE100 + 21)
                        # blt.put(x, y, '.')
                        # Draw forest tiles

                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if game_map.tiles[x][y].forest:
                        blt.layer(0)
                        blt.color("darkest gray")
                        blt.put(x, y, 0xE100 + 21)
                        blt.layer(1)
                        blt.color("darkest gray")
                        if game_map.tiles[x][y].seed < 50:
                            blt.color("darkest gray")
                        if 0 <= game_map.tiles[x][y].seed <= int(100 / 6):
                            blt.put(x, y, 0xE100 + 87)
                        if int(100 / 6) <= game_map.tiles[x][y].seed <= 100 / 6 * 2:
                            blt.put(x, y, 0xE100 + 88)
                        if int(100 / 6 * 2) <= game_map.tiles[x][y].seed <= 100 / 6 * 3:
                            blt.put(x, y, 0xE100 + 89)
                        if int(100 / 6 * 3) <= game_map.tiles[x][y].seed <= 100 / 6 * 4:
                            blt.put(x, y, 0xE100 + 93)
                        if int(100 / 6 * 4) <= game_map.tiles[x][y].seed <= 100 / 6 * 5:
                            blt.put(x, y, 0xE100 + 94)
                        if int(100 / 6 * 5) <= game_map.tiles[x][y].seed <= 100:
                            blt.put(x, y, 0xE100 + 95)

                    else:
                        # Draw floor tiles
                        blt.color("darkest gray")
                        blt.put(x, y, 0xE100 + 21)

                    # blt.put(x, y, 'T')
                # Draw wall tiles
                # elif game_map.tiles[x][y].blocked:
                #    blt.color(None)
                #    blt.layer(1)
                #    blt.put(x, y, 0xE100 + 83)
                #    # blt.put(x, y, '#')


def draw_all(game_map, game_camera, entities, px, py, fov_map, fov_recompute):

    # game_camera.move_camera(
    #    px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera, fov_map, fov_recompute)
    draw_entities(entities, game_map, game_camera)


def clear_entities(entities, game_camera):

    for entity in entities:
        #x, y = game_camera.get_coordinates(entity.x, entity.y)
        clear(entity, entity.x, entity.y)


def draw(entity, game_map, camera_x, camera_y):

    if not game_map.tiles[entity.x][entity.y].blocked:
        # Draw the entity to the screen
        blt.layer(entity.layer)
        blt.color(blt.color_from_name(entity.color))
        blt.put(entity.x, entity.y, entity.char)


def clear(entity, camera_x, camera_y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.put(entity.x, entity.y, " ")
