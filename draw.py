from bearlibterminal import terminal as blt


def draw_entities(entities, game_map, game_camera):

    for entity in entities:
        camera_x, camera_y = game_camera.get_coordinates(entity.x, entity.y)
        draw(entity, game_map, camera_x, camera_y)


def draw_map(game_map, game_camera):

    # Draw all the tiles in the game map
    for y in range(game_camera.height):
        for x in range(game_camera.width):
            map_x, map_y = game_camera.x + x, game_camera.y + y

            # Draw floor tiles
            blt.color("darkest amber")
            blt.put(x, y, 0xE100 + 21)
            # blt.put(x, y, '.')
            # Draw forest tiles
            if game_map.tiles[map_x][map_y].forest:
                blt.layer(0)
                blt.color("darkest amber")
                blt.put(x, y, 0xE100 + 21)
                blt.layer(1)
                blt.color("light orange")
                if game_map.tiles[map_x][map_y].seed < 50:
                    blt.color("orange")
                if 0 <= game_map.tiles[map_x][map_y].seed <= int(100 / 6):
                    blt.put(x, y, 0xE100 + 87)
                if int(100 / 6) <= game_map.tiles[map_x][map_y].seed <= 100 / 6 * 2:
                    blt.put(x, y, 0xE100 + 88)
                if int(100 / 6 * 2) <= game_map.tiles[map_x][map_y].seed <= 100 / 6 * 3:
                    blt.put(x, y, 0xE100 + 89)
                if int(100 / 6 * 3) <= game_map.tiles[map_x][map_y].seed <= 100 / 6 * 4:
                    blt.put(x, y, 0xE100 + 93)
                if int(100 / 6 * 4) <= game_map.tiles[map_x][map_y].seed <= 100 / 6 * 5:
                    blt.put(x, y, 0xE100 + 94)
                if int(100 / 6 * 5) <= game_map.tiles[map_x][map_y].seed <= 100:
                    blt.put(x, y, 0xE100 + 95)
               #    blt.put(x, y, 0xE100 + choice([i for i in range(87, 96)
               #                                  if i not in [90, 91, 92]]))

                # blt.put(x, y, 'T')
            # Draw wall tiles
            # elif game_map.tiles[x][y].blocked:
            #    blt.color(None)
            #    blt.layer(1)
            #    blt.put(x, y, 0xE100 + 83)
            #    # blt.put(x, y, '#')


def draw_all(game_map, game_camera, entities, px, py):

    game_camera.move_camera(
        px, py, game_map.width, game_map.height)
    draw_map(game_map, game_camera)
    draw_entities(entities, game_map, game_camera)


def clear_entities(entities, game_camera):

    for entity in entities:
        map_x, map_y = game_camera.get_coordinates(entity.x, entity.y)
        clear(entity, map_x, map_y)


def draw(entity, game_map, camera_x, camera_y):

    if not game_map.tiles[entity.x][entity.y].blocked:
        # Draw the entity to the screen
        blt.layer(entity.layer)
        blt.color(blt.color_from_name(entity.color))
        blt.put(camera_x, camera_y, entity.char)


def clear(entity, camera_x, camera_y):
    # Clear the entity from the screen
    blt.layer(entity.layer)
    blt.put(camera_x, camera_y, " ")
