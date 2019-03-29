# import tcod as libtcodpy
from bearlibterminal import terminal as blt
from camera import Camera
from draw import draw_all, clear_entities
from entity import Entity
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from random import randint

WINDOW_WIDTH = 40
WINDOW_HEIGHT = 30
MAP_WIDTH = 200
MAP_HEIGHT = 200


def blt_init():

    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=' + str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)
    title = 'title=' + window_title
    cellsize = 'cellsize=32x32'
    resizable = 'resizable=true'
    window = "window: " + size + "," + title + "," + cellsize + "," + resizable

    blt.set(window)
    # Load tilesets
    blt.set("U+E100: ./tilesets/adam_bolt_angband16x16_fix.png, size=16x16,"
            "resize=32x32, resize-filter=nearest, align=top-left")
    blt.clear()


def player_init(game_map):

    px = randint(1, game_map.width)
    py = randint(1, game_map.height)

    return px, py


def game_loop():
    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
    px, py = player_init(game_map)
    if game_map.is_blocked(px, py):
        px, py = player_init(game_map)
    player = Entity(px, py, 2, 0xE100 + 704, None)
    # npc = Entity(int(WINDOW_WIDTH / 2 - 5),
    #             int(WINDOW_HEIGHT / 2 - 5), 1, 0xE100 + 1829, None)
    entities = [player]
    game_camera = Camera(player.x, player.y, WINDOW_WIDTH, WINDOW_HEIGHT)
    draw_all(game_map, game_camera, entities, player.x, player.y)

    key = None
    while key not in (blt.TK_CLOSE, blt.TK_ESCAPE):

        blt.refresh()

        key = blt.read()
        clear_entities(entities, game_camera)
        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if exit:
            blt.close()

        if fullscreen:
            blt.set("window.fullscreen=true")

        draw_all(game_map, game_camera, entities, player.x, player.y)

    blt.close()


if __name__ == '__main__':
    blt_init()
    game_loop()
