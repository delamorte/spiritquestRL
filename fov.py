from tcod import map


def initialize_fov(game_map):
    fov_map = map.Map(game_map.width, game_map.height)
    fov_map.walkable[:] = True
    fov_map.transparent[:] = True

    for y in range(game_map.height):
        for x in range(game_map.width):
            if game_map.tiles[x][y].blocked:
                fov_map.walkable[y, x] = False
            if game_map.tiles[x][y].block_sight:
                fov_map.transparent[y, x] = False

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    fov_map.compute_fov(x, y, radius, light_walls, algorithm)
