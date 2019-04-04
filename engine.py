from bearlibterminal import terminal as blt
from camera import Camera
from draw import draw_all, clear_entities
from entity import Entity
from fov import initialize_fov, recompute_fov
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from random import randint

WINDOW_WIDTH = 128
WINDOW_HEIGHT = 60
MAP_WIDTH = 200
MAP_HEIGHT = 200
FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 6


def blt_init():

    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=' + str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)
    title = 'title=' + window_title
    cellsize = 'cellsize=auto'
    resizable = 'resizable=true'
    window = "window: " + size + "," + title + "," + cellsize + "," + resizable

    blt.set(window)
    blt.set("font: default")
    # Load tilesets
    blt.set("U+E100: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=32x32, resize-filter=nearest, align=top-left")
    blt.clear()


def level_init(game_map):

    # Initialize player, starting position and other entities
    px, py = randint(1, game_map.width - 1), \
        randint(1, game_map.height - 1)
    while game_map.is_blocked(px, py):
        px, py = randint(1, game_map.width - 1), \
            randint(1, game_map.height - 1)
    player = Entity(px, py, 2, 0xE100 + 1587, None)
    if game_map.name == "hub":
        player.char = 0xE100 + 704
        for x in range(game_map.width - 1):
            for y in range(game_map.height - 1):
                if game_map.tiles[x][y].spawnable:
                    player.x = x - 1
                    player.y = y - 1
    if game_map.name == "debug":
        player.x, player.y = 2, 2
    player.spirit_power = 200
    # npc = Entity(int(WINDOW_WIDTH / 2 - 5),
    #             int(WINDOW_HEIGHT / 2 - 5), 1, 0xE100 + 1829, None)
    entities = [player]

    # Initialize game camera
    game_camera = Camera(player.x, player.y,
                         int(WINDOW_WIDTH / 4),
                         int(WINDOW_HEIGHT / 2 - 5))
    # Initialize field of view
    fov_map = initialize_fov(game_map)

    return game_map, game_camera, entities, player, fov_map


def level_change(level_name, levels):

    if level_name == "hub":
        game_map = levels[0]
        game_map, game_camera, entities, player, fov_map = level_init(game_map)

    if level_name == "dream":
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT, "dream")
        game_map.generate_forest(0, 0, game_map.width, game_map.height, 25, block_sight=True)
        levels.append(game_map)
        game_map, game_camera, entities, player, fov_map = level_init(game_map)

    if level_name == "debug":
        game_map = levels[2]
        game_map, game_camera, entities, player, fov_map = level_init(game_map)

    return game_map, game_camera, entities, player, fov_map


def game_loop():

    blt_init()
    game_map_hub = GameMap(MAP_WIDTH, MAP_HEIGHT, "hub")
    game_map_hub.generate_hub()
    # Initialize map
    game_map_dream = GameMap(MAP_WIDTH, MAP_HEIGHT, "dream")
    game_map_dream.generate_forest(
        0, 0, game_map_dream.width, game_map_dream.height, 25, block_sight=True)

    # Set debug level
    # game_map_debug = GameMap(int(WINDOW_WIDTH / 4),
    #                         int(WINDOW_HEIGHT / 2 - 5), "debug")
    # levels = [game_map_hub, game_map_dream, game_map_debug]

    levels = [game_map_hub, game_map_dream]
    game_map, game_camera, entities, player, fov_map = level_change(
        "hub", levels)
    fov_recompute = True
    message_log = []

    key = None
    while key not in (blt.TK_CLOSE, blt.TK_ESCAPE):

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, FOV_RADIUS,
                          FOV_LIGHT_WALLS, FOV_ALGORITHM)

        draw_all(game_map, game_camera, entities, player.x,
                 player.y, fov_map, fov_recompute, message_log)
        fov_recompute = False
        blt.layer(2)
        blt.printf(2, 2, "Spirit power left: " + str(player.spirit_power))
        blt.refresh()

        key = blt.read()
        clear_entities(entities, game_camera)
        action = handle_keys(key)

        move = action.get('move')
        stairs = action.get('stairs')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)
                if (game_map.name is not "hub" and
                        game_map.name is not "debug"):
                    player.spirit_power -= 1
                fov_recompute = True
            if game_map.tiles[player.x + dx][player.y + dy].char == 0xE100 + 67:
                message_log.append("The door is locked...")
            if game_map.tiles[player.x][player.y].char == 0xE100 + 427:
                message_log.append(
                    "Meditate and go to dream world with '<' or '>'")

        if exit:
            blt.close()

        if fullscreen:
            blt.set("window.fullscreen=true")

        if player.spirit_power <= 0:
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels)
            message_log.append("I have no power to meditate longer..")

        if stairs:
            if game_map.tiles[player.x][player.y].char == 0xE100 + 427:
                game_map, game_camera, entities, player, fov_map = \
                    level_change("dream", levels)
                message_log.append("I'm dreaming... I feel my spirit power draining..")
                fov_recompute = True
    blt.close()


if __name__ == '__main__':
    game_loop()
