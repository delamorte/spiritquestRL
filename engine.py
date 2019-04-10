from bearlibterminal import terminal as blt
from camera import Camera
from draw import draw_all, draw_ui, clear_entities, clear_camera
from entity import blocking_entity
from game_states import GameStates
from fov import initialize_fov, recompute_fov
from input_handlers import handle_keys
from manual_cellsize import test_manual_cellsize
from map_objects.game_map import GameMap
from math import floor
from ui.elements import Panel
from ui.game_messages import MessageLog
from ui.message_history import show_msg_history
from sys import exit

"""
TODO:

- Improve UI
- Items and inventory
- Npcs
- Make maps more interesting
- Minimap
- Put tileset to dictionary and put corresponding
  ascii symbols
- Menus
- Saving and loading
- Combat
- Dying and winning
- New game and character creation

FIX:

- Make FOV variables non global and changeable (fov class?)
- Generate levels with a seed

"""
MAP_WIDTH = 50
MAP_HEIGHT = 50
FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 6


def blt_init():

    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=120x48'
    title = 'title=' + window_title
    cellsize = 'cellsize=auto'
    resizable = 'resizeable=false'
    window = "window: " + size + "," + title + "," + cellsize + "," + resizable

    blt.set(window)
    blt.set("font: default")
    # Load tilesets
    blt.set("U+E100: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=32x32, resize-filter=nearest, align=top-left")
    blt.clear()


def level_init(game_map):

    # Initialize entities
    player, entities = game_map.place_entities()

    # Initialize game camera
    game_camera = Camera(1, 1, floor(blt.state(blt.TK_WIDTH) / 4),
                         floor(blt.state(blt.TK_HEIGHT) / 2 - 5))
    # Initialize field of view
    fov_map = initialize_fov(game_map)

    return game_map, game_camera, entities, player, fov_map


def level_change(level_name, levels):

    if not levels:
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT, "hub")
        game_map.generate_hub()
        levels.append(game_map)

    if level_name is "hub":
        for level in levels:
            if level.name is level_name:
                game_map = level
        game_map, game_camera, entities, player, fov_map = level_init(game_map)

    if level_name is "dream":
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT, "dream")
        game_map.generate_forest(0, 0, game_map.width,
                                 game_map.height, 25, block_sight=True)
        game_map, game_camera, entities, player, fov_map = level_init(game_map)

    # Set debug level
    if level_name is "debug":
        game_map = GameMap(floor(blt.state(blt.TK_WIDTH) / 4),
                           floor(blt.state(blt.TK_HEIGHT) / 2 - 5), "debug")
        game_map, game_camera, entities, player, fov_map = level_init(game_map)

    return game_map, game_camera, entities, player, fov_map


def init_ui():

    screen_w = blt.state(floor(blt.TK_WIDTH))
    screen_h = blt.state(floor(blt.TK_HEIGHT))
    w = floor(screen_w / 4)
    h = floor(screen_h / 2 - 5)

    msg_panel = Panel(1, h + 1, w - 1, h + 4)
    msg_panel_borders = Panel(0, h, w, h + 5)
    screen_borders = Panel(0, 0, w, h)

    viewport_x = w * 4 - 5
    viewport_y = h * 2 - 3
    return viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders


def main_menu(viewport_x, viewport_y):

    current_range = 0
    center_x = int(viewport_x / 2)
    center_y = int(viewport_y / 2)
    while True:

        choices = ["New game", "Resize window", "Exit"]
        blt.layer(0)
        clear_camera(viewport_x, viewport_y)
        blt.puts(center_x+2, center_y, "[color=white]Spirit Quest RL", 0, 0, blt.TK_ALIGN_CENTER)

        for i, r in enumerate(choices):
            selected = i == current_range
            blt.color("orange" if selected else "light_gray")
            blt.puts(center_x+2, center_y + 2 + i, "%s%s" %
                     ("[U+203A]" if selected else " ", r), 0, 0, blt.TK_ALIGN_CENTER)

        blt.refresh()

        r = choices[current_range]

        key = blt.read()
        if key in (blt.TK_ESCAPE, blt.TK_CLOSE):
            exit()
        if key == blt.TK_ENTER and r is "New game":
            break
        elif key == blt.TK_ENTER and r is "Exit":
            exit()
        elif key == blt.TK_ENTER and r is "Resize window":
            blt.set("window: resizeable=true, minimum-size=40x20")
            key = None
            while key not in (blt.TK_CLOSE, blt.TK_ESCAPE, blt.TK_ENTER):
                viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
                center_x = int(viewport_x / 2)
                center_y = int(viewport_y / 2)
                draw_ui(viewport_x, viewport_y, msg_panel,
                        msg_panel_borders, screen_borders)
                clear_camera(viewport_x, viewport_y)
                blt.puts(center_x + 2, center_y,
                             "[color=white]Resize window by dragging from borders.\n Alt+Enter for fullscreen.\n Press Enter or Esc when done.", 0, 0, blt.TK_ALIGN_CENTER)
                blt.refresh()

                key = blt.read()
                if key == blt.TK_FULLSCREEN:
                    blt.set("window.fullscreen=true")
            blt.set("window: resizeable=false")
        elif key == blt.TK_UP:
            if current_range > 0:
                current_range -= 1
        elif key == blt.TK_DOWN:
            if current_range < len(choices) - 1:
                current_range += 1


def main():

    blt_init()

    levels = []
    game_map, game_camera, entities, player, fov_map = level_change(
        "hub", levels)

    fov_recompute = True
    viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
    draw_ui(viewport_x, viewport_y, msg_panel,
            msg_panel_borders, screen_borders)
    message_log = MessageLog(5)
    power_msg = "Spirit power left: " + str(player.spirit_power)
    main_menu(viewport_x, viewport_y)
    turn_count = 0
    game_state = GameStates.PLAYER_TURN
    key = None
    while key not in (blt.TK_CLOSE, blt.TK_ESCAPE):

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, FOV_RADIUS,
                          FOV_LIGHT_WALLS, FOV_ALGORITHM)

        draw_all(game_map, game_camera, entities, player.x,
                 player.y, fov_map, fov_recompute, message_log, msg_panel, power_msg, viewport_x, viewport_y)

        fov_recompute = False
        blt.refresh()

        key = blt.read()
        clear_entities(entities, game_camera)
        action = handle_keys(key)

        move = action.get('move')
        stairs = action.get('stairs')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = blocking_entity(
                    entities, destination_x, destination_y)
                if target:
                    player.spirit_power -= 1
                    if target.name is "Snake":
                        message_log.send("I feel my power returning!")
                        player.spirit_power += 11
                        power_msg = "Spirit power left: " + \
                            str(player.spirit_power)
                        entities.remove(target)
                else:
                    player.move(dx, dy)

                    if (game_map.name is not "hub" and
                            game_map.name is not "debug"):
                        player.spirit_power -= 1
                        power_msg = "Spirit power left: " + \
                            str(player.spirit_power)

                    if game_map.tiles[player.x][player.y].char == 0xE100 + 427:
                        message_log.send(
                            "Meditate and go to dream world with '<' or '>'")
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

            if game_map.tiles[destination_x][destination_y].char == \
                    0xE100 + 67:
                message_log.send("The door is locked...")
                game_state = GameStates.ENEMY_TURN

        if exit:
            exit()

        if fullscreen:
            blt.set("window.fullscreen=true")

        if player.spirit_power <= 0:
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels)
            message_log.clear()
            message_log.send("I have no power to meditate longer..")
            player.spirit_power = 20
            power_msg = "Spirit power left: " + \
                        str(player.spirit_power)

        if player.spirit_power >= 30:
            message_log.send("My spirit has granted me new insights!")
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels)
            for y in range(game_map.height):
                for x in range(game_map.width):
                    if game_map.tiles[x][y].char == 0xE100 + 67:
                        game_map.tiles[x][y].char = 0xE100 + 68
                        game_map.tiles[x][y].blocked = False

        if stairs:
            if game_map.tiles[player.x][player.y].char == 0xE100 + 427:
                game_map, game_camera, entities, player, fov_map = \
                    level_change("dream", levels)
                message_log.clear()
                message_log.send(
                    "I'm dreaming... I feel my spirit power draining.")
                message_log.send("I'm hungry..")
                fov_recompute = True
        if key == blt.TK_M:
            show_msg_history(
                message_log.history, viewport_x, viewport_y)
            draw_ui(viewport_x, viewport_y, msg_panel,
                    msg_panel_borders, screen_borders)
            fov_recompute = True

        if game_state == GameStates.ENEMY_TURN:

            for entity in entities:
                if entity != player and turn_count == 0:
                    message_log.send("You sense a snake hiding in the woods.")
                    turn_count += 1
            game_state = GameStates.PLAYER_TURN

    blt.close()


if __name__ == '__main__':
    main()
