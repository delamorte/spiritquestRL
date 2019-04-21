from bearlibterminal import terminal as blt
from camera import Camera
from death_functions import kill_monster, kill_player
from draw import draw_all, draw_ui, clear_entities, clear_camera
from entity import Entity, blocking_entity
from game_states import GameStates
from fov import initialize_fov, recompute_fov
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from math import floor
from map_objects.tilemap import tilemap
from ui.elements import Panel
from ui.game_messages import MessageLog
from ui.message_history import show_msg_history
from sys import exit
import options

"""
TODO:

- Items and inventory
- Npcs
- Minimap
- Saving and loading

FIX:

- Make FOV variables non global and changeable (fov class?)
- Generate levels with a seed

"""
MAP_WIDTH = 100
MAP_HEIGHT = 100
FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 6


def blt_init():

    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=128x50'
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


def level_init(game_map, player):

    # Initialize entities
    player, entities = game_map.place_entities(player)

    # Initialize game camera
    game_camera = Camera(1, 1, floor(blt.state(blt.TK_WIDTH) / 4),
                         floor(blt.state(blt.TK_HEIGHT) / 2 - 5))
    # Initialize field of view
    fov_map = initialize_fov(game_map)

    return game_map, game_camera, entities, player, fov_map


def level_change(level_name, levels, player):

    if not levels:
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT, "hub")
        game_map.generate_hub()
        levels.append(game_map)

    if level_name is "hub":
        for level in levels:
            if level.name is level_name:
                game_map = level
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)

    if level_name is "dream":
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT, "dream")
        game_map.generate_forest()
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)

    # Set debug level
    if level_name is "debug":
        game_map = GameMap(50, 50, "debug")
        # game_map.generate_trees(0, 0, game_map.width,
        #                        game_map.height, 20, block_sight=True)
        game_map.generate_forest()
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)

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

        choices = ["New game", "Resize window",
                   "Graphics: " + options.gfx, "Exit"]
        blt.layer(0)
        clear_camera(viewport_x, viewport_y)
        blt.puts(center_x + 2, center_y,
                 "[color=white]Spirit Quest RL", 0, 0, blt.TK_ALIGN_CENTER)

        for i, r in enumerate(choices):
            selected = i == current_range
            blt.color("orange" if selected else "light_gray")
            blt.puts(center_x + 2, center_y + 2 + i, "%s%s" %
                     ("[U+203A]" if selected else " ", r), 0, 0, blt.TK_ALIGN_CENTER)

        blt.refresh()

        r = choices[current_range]

        key = blt.read()
        if key in (blt.TK_ESCAPE, blt.TK_CLOSE):
            exit()

        if key == blt.TK_ENTER and current_range == 2:
            if options.gfx is "tiles":
                options.gfx = "ascii"
            elif options.gfx is "ascii":
                options.gfx = "tiles"

        if key == blt.TK_ENTER and r is "New game":
            while True:
                clear_camera(viewport_x, viewport_y)
                animals = tilemap()["monsters"]
                blt.layer(0)
                blt.puts(center_x + 2, center_y,
                         "[color=white]Choose your spirit animal...", 0, 0, blt.TK_ALIGN_CENTER)
                for i, (r, c) in enumerate(animals.items()):
                    selected = i == current_range
                    blt.color("orange" if selected else "default")
                    blt.puts(center_x - 10, center_y + 2 + i * 2, "%s%s" %
                             ("[U+203A]" if selected else " ", r.capitalize()), 0, 0)
                    blt.layer(0)
                    blt.put_ext(center_x - 2, center_y +
                                2 + i * 2, 0, -8, 0xE100 + 3)
                    blt.layer(1)
                    blt.put_ext(center_x - 2, center_y + 2 + i * 2, 0, -8, c)
                    if selected:
                        choice = r

                blt.refresh()
                key = blt.read()

                if key in (blt.TK_ESCAPE, blt.TK_CLOSE):
                    main_menu(viewport_x, viewport_y)
                elif key == blt.TK_UP:
                    if current_range > 0:
                        current_range -= 1
                elif key == blt.TK_DOWN:
                    if current_range < len(animals) - 1:
                        current_range += 1
                elif key == blt.TK_ENTER:
                    player = Entity(
                        1, 1, 50, animals[choice], None, choice, blocks=True, player=True, fighter=True)
                    return player

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
                         "[color=white]Use arrow keys or drag window borders to resize.\n Alt+Enter for fullscreen.\n Press Enter or Esc when done.", 0, 0, blt.TK_ALIGN_CENTER)
                blt.refresh()

                key = blt.read()
                if key == blt.TK_FULLSCREEN:
                    blt.set("window.fullscreen=true")
                if key == blt.TK_UP:
                    h = blt.state(blt.TK_HEIGHT)
                    w = blt.state(blt.TK_WIDTH)
                    blt.set("window: size=" + str(w) + "x" + (str(h + 2)))
                if key == blt.TK_DOWN:
                    h = blt.state(blt.TK_HEIGHT)
                    w = blt.state(blt.TK_WIDTH)
                    blt.set("window: size=" + str(w) + "x" + (str(h - 2)))
                if key == blt.TK_RIGHT:
                    h = blt.state(blt.TK_HEIGHT)
                    w = blt.state(blt.TK_WIDTH)
                    blt.set("window: size=" + (str(w + 4)) + "x" + str(h))
                if key == blt.TK_LEFT:
                    h = blt.state(blt.TK_HEIGHT)
                    w = blt.state(blt.TK_WIDTH)
                    blt.set("window: size=" + (str(w - 4)) + "x" + str(h))
            blt.set("window: resizeable=false")
        elif key == blt.TK_UP:
            if current_range > 0:
                current_range -= 1
        elif key == blt.TK_DOWN:
            if current_range < len(choices) - 1:
                current_range += 1


def main():

    blt_init()
    fov_recompute = True
    viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
    draw_ui(viewport_x, viewport_y, msg_panel,
            msg_panel_borders, screen_borders)
    message_log = MessageLog(5)
    player = main_menu(viewport_x, viewport_y)
    levels = []
    game_map, game_camera, entities, player, fov_map = level_change(
        "dream", levels, player)
    power_msg = "Spirit power left: " + str(player.spirit_power)
    turn_count = 0
    game_state = GameStates.PLAYER_TURN
    key = None
    while key not in (blt.TK_CLOSE, blt.TK_ESCAPE):

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, FOV_RADIUS,
                          FOV_LIGHT_WALLS, FOV_ALGORITHM)

        draw_all(game_map, game_camera, entities, player, player.x, player.y,
                 fov_map, fov_recompute, message_log, msg_panel, power_msg,
                 viewport_x, viewport_y)

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
                    combat_msg = player.fighter_c.attack(target)
                    message_log.send(combat_msg)
                    player.spirit_power -= 1
                    if target.fighter_c.hp <= 0:
                        entities.remove(target)
                        message_log.send("I feel my power returning!")
                        player.spirit_power += 11
                        player.fighter_c.hp += target.fighter_c.power
                        power_msg = "Spirit power left: " + \
                            str(player.spirit_power)
                else:
                    player.move(dx, dy)

                    if (game_map.name is not "hub" and
                            game_map.name is not "debug"):
                        player.spirit_power -= 1
                        power_msg = "Spirit power left: " + \
                            str(player.spirit_power)

                    if game_map.tiles[player.x][player.y].char == tilemap()["campfire"]:
                        message_log.send(
                            "Meditate and go to dream world with '<' or '>'")
                    fov_recompute = True
                turn_count += 1
                game_state = GameStates.ENEMY_TURN

            if game_map.tiles[destination_x][destination_y].char == \
                    tilemap()["door_closed"]:
                message_log.send("The door is locked...")
                turn_count += 1
                game_state = GameStates.ENEMY_TURN

        if key == blt.TK_PERIOD or key == blt.TK_KP_5:
            turn_count += 1
            player.spirit_power -= 1
            power_msg = "Spirit power left: " + \
                str(player.spirit_power)
            game_state = GameStates.ENEMY_TURN

        if exit:
            exit()

        if fullscreen:
            blt.set("window.fullscreen=true")

        if player.spirit_power <= 0:
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels, player)
            message_log.clear()
            message_log.send("I have no power to meditate longer..")
            player.spirit_power = 50
            player.fighter_c.hp = player.fighter_c.max_hp
            power_msg = "Spirit power left: " + \
                str(player.spirit_power)

        if player.spirit_power >= 60:
            message_log.send("My spirit has granted me new insights!")
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels, player)

            # Currently opens the door in hub
            for y in range(game_map.height):
                for x in range(game_map.width):
                    if game_map.tiles[x][y].char == tilemap()["door_closed"]:
                        game_map.tiles[x][y].char = tilemap()["door_open"]
                        game_map.tiles[x][y].blocked = False

        if stairs:
            if game_map.tiles[player.x][player.y].char == tilemap()["campfire"]:
                game_map, game_camera, entities, player, fov_map = level_change(
                    "dream", levels, player)
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
                if entity.ai:
                    combat_msg = entity.ai_c.take_turn(
                        player, fov_map, game_map, entities)
                    if combat_msg:
                        message_log.send(combat_msg)
                if entity.fighter_c.dead:
                    if entity.player:
                        kill_msg, game_state = kill_player(player)
                        message_log.send(kill_msg)
                    else:
                        message_log.send(kill_monster(entity))
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            if not game_state == GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN

    blt.close()


if __name__ == '__main__':
    main()
