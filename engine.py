from bearlibterminal import terminal as blt
from camera import Camera
from collections import Counter
from death_functions import kill_monster, kill_player
from draw import draw_all, draw_stats, draw_ui, clear_entities, clear_camera
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
import variables

"""
TODO:

- Improve combat mechanics
- Items and inventory
- Npcs
- Minimap
- Saving and loading
- Examine/view mode

FIX:

- Make FOV variables non global and changeable (fov class?)
- Generate levels with a seed

"""
MAP_WIDTH = 100
MAP_HEIGHT = 100


def blt_init():

    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=128x50'
    title = 'title=' + window_title
    cellsize = 'cellsize=auto'
    tilesize = variables.tilesize + 'x' + variables.tilesize
    ui_size = variables.ui_size + 'x' + variables.ui_size
    resizable = 'resizeable=false'
    window = "window: " + size + "," + title + "," + cellsize + "," + resizable

    blt.set(window)
    blt.set("font: default")
    # Load tilesets
    blt.set("U+E100: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=" + tilesize + ", resize-filter=nearest, align=top-left")
    blt.set("U+E900: ./tilesets/adam_bolt_angband16x16_fix.png, \
        size=16x16, resize=" + ui_size + ", resize-filter=nearest, align=top-left")
    variables.tile_offset_x = int(
        int(variables.tilesize) / blt.state(blt.TK_CELL_WIDTH))
    variables.tile_offset_y = int(
        int(variables.tilesize) / blt.state(blt.TK_CELL_HEIGHT))
    variables.ui_offset_x = int(
        int(variables.ui_size) / blt.state(blt.TK_CELL_WIDTH))
    variables.ui_offset_y = int(
        int(variables.ui_size) / blt.state(blt.TK_CELL_HEIGHT))
    variables.camera_offset = int(variables.ui_size) / int(variables.tilesize)
    blt.clear()


def level_init(game_map, player):

    # Initialize entities
    player, entities = game_map.place_entities(player)

    # Initialize game camera
    game_camera = Camera(1, 1, int(floor(blt.state(blt.TK_WIDTH) / variables.ui_offset_x) * variables.camera_offset),
                         int(floor(blt.state(blt.TK_HEIGHT) / variables.ui_offset_y - 5) * variables.camera_offset))
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
        game_map = GameMap(100, 100, "debug")
        # game_map.generate_trees(0, 0, game_map.width,
        #                        game_map.height, 20, block_sight=True)
        # game_map.generate_forest()
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)

    return game_map, game_camera, entities, player, fov_map


def init_ui():

    screen_w = blt.state(floor(blt.TK_WIDTH))
    screen_h = blt.state(floor(blt.TK_HEIGHT))

    w = floor(screen_w / variables.ui_offset_x)
    h = floor(screen_h / variables.ui_offset_y - 5)

    msg_panel = Panel(1, h + 1, w - 1, h + 4)
    msg_panel_borders = Panel(0, h, w, h + 5)
    screen_borders = Panel(0, 0, w, h)

    viewport_x = w * variables.ui_offset_x - (variables.ui_offset_x + 1)
    viewport_y = h * variables.ui_offset_y - (variables.ui_offset_y + 1)
    return viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders


def main_menu(viewport_x, viewport_y, msg_panel):

    current_range = 0
    center_x = int(viewport_x / 2)
    center_y = int(viewport_y / 2)
    while True:

        choices = ["New game", "Resize window",
                   "Graphics: " + variables.gfx, "Tilesize: " + variables.tilesize + "x" + variables.tilesize, "Exit"]
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
            if variables.gfx is "tiles":
                variables.gfx = "ascii"
            elif variables.gfx is "ascii":
                variables.gfx = "tiles"

        if key == blt.TK_ENTER and current_range == 3:
            if int(variables.tilesize) < 48:
                variables.tilesize = str(int(variables.tilesize) + 16)
                blt.close()
                blt_init()
                viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
            else:
                variables.tilesize = str(16)
                blt.close()
                blt_init()
                viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
                draw_ui(msg_panel, msg_panel_borders, screen_borders)

        if key == blt.TK_ENTER and r is "New game":
            key = None
            while True:
                clear_camera(viewport_x, viewport_y)
                animals = tilemap()["monsters"]
                blt.layer(0)
                blt.puts(center_x + 2, center_y,
                         "[color=white]Choose your spirit animal...", 0, 0, blt.TK_ALIGN_CENTER)
                for i, (r, c) in enumerate(animals.items()):
                    selected = i == current_range
                    blt.color("orange" if selected else "default")
                    blt.puts(center_x - 10, center_y + 2 + i * variables.tile_offset_y, "%s%s" %
                             ("[U+203A]" if selected else " ", r.capitalize()), 0, 0)
                    blt.layer(0)
                    blt.put_ext(center_x - 2, center_y +
                                2 + i * variables.tile_offset_y, 0, -8, 0xE100 + 3)
                    blt.layer(1)
                    blt.put_ext(center_x - 2, center_y + 2 + i *
                                variables.tile_offset_y, 0, -8, c)
                    if selected:
                        choice = r

                blt.refresh()
                key = blt.read()

                if key in (blt.TK_ESCAPE, blt.TK_CLOSE):
                    main_menu(viewport_x, viewport_y, msg_panel)
                elif key == blt.TK_UP:
                    if current_range > 0:
                        current_range -= 1
                elif key == blt.TK_DOWN:
                    if current_range < len(animals) - 1:
                        current_range += 1
                elif key == blt.TK_ENTER:
                    player = Entity(
                        1, 1, 12, animals[choice], None, choice, blocks=True, player=True, fighter=True)
                    return player, viewport_x, viewport_y, msg_panel

        elif key == blt.TK_ENTER and r is "Exit":
            exit()

        elif key == blt.TK_ENTER and r is "Resize window":
            blt.set("window: resizeable=true, minimum-size=60x20")
            key = None
            while key not in (blt.TK_CLOSE, blt.TK_ESCAPE, blt.TK_ENTER):
                viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
                center_x = int(viewport_x / 2)
                center_y = int(viewport_y / 2)
                h = blt.state(blt.TK_HEIGHT)
                w = blt.state(blt.TK_WIDTH)
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
                clear_camera(viewport_x, viewport_y)
                blt.puts(center_x + 2, center_y,
                         "[color=white]Use arrow keys or drag window borders to resize.\n Alt+Enter for fullscreen.\n Press Enter or Esc when done.", 0, 0, blt.TK_ALIGN_CENTER)
                blt.refresh()

                key = blt.read()
                if key == blt.TK_FULLSCREEN:
                    blt.set("window.fullscreen=true")
                if key == blt.TK_UP:
                    blt.set("window: size=" + str(w) + "x" +
                            (str(h + variables.tile_offset_y)))
                if key == blt.TK_DOWN:
                    blt.set("window: size=" + str(w) + "x" +
                            (str(h - variables.tile_offset_y)))
                    if h <= 30:
                        blt.set("window: size=" + str(w) + "x" + "30")
                if key == blt.TK_RIGHT:
                    blt.set("window: size=" +
                            (str(w + variables.tile_offset_x)) + "x" + str(h))
                if key == blt.TK_LEFT:
                    blt.set("window: size=" +
                            (str(w - variables.tile_offset_x)) + "x" + str(h))
                    if w <= 60:
                        blt.set("window: size=60" + "x" + str(h))

            blt.set("window: resizeable=false")
        elif key == blt.TK_UP:
            if current_range > 0:
                current_range -= 1
        elif key == blt.TK_DOWN:
            if current_range < len(choices) - 1:
                current_range += 1


def main():

    fov_recompute = True
    viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
    draw_ui(msg_panel, msg_panel_borders, screen_borders)
    message_log = MessageLog(5)
    player, viewport_x, viewport_y, msg_panel = main_menu(
        viewport_x, viewport_y, msg_panel)
    levels = []
    game_map, game_camera, entities, player, fov_map = level_change(
        "dream", levels, player)
    power_msg = "Spirit power left: " + str(player.spirit_power)
    time_counter = variables.TimeCounter()
    insights = 600
    game_state = GameStates.PLAYER_TURN
    key = None
    while True:
        print(str(time_counter.turn))
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, player.fov, True, 0)

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
                    player.spirit_power -= 0.5
                    time_counter.take_turn(1)
                    draw_stats(player, viewport_x,
                               viewport_y, power_msg, target)

                else:
                    player.move(dx, dy)

                    time_counter.take_turn(1 / player.fighter_c.mv_spd)

                    if (game_map.name is not "hub" and
                            game_map.name is not "debug"):
                        #player.spirit_power -= 0.5
                        power_msg = "Spirit power left: " + \
                            str(player.spirit_power)
                        draw_stats(player, viewport_x, viewport_y, power_msg)

                    if game_map.tiles[player.x][player.y].char == tilemap()["campfire"]:
                        message_log.send(
                            "Meditate and go to dream world with '<' or '>'")

                    # If there are entities under the player, print them
                    stack = []
                    for entity in entities:
                        if not entity.fighter_c:
                            if player.x == entity.x and player.y == entity.y:
                                stack.append(entity.name)
                    
                    if len(stack) > 0:
                        d = dict(Counter(stack))
                        formatted_stack = []
                        for i in d:
                            if d[i] > 1:
                                formatted_stack.append(i + " x" + str(d[i]))
                            else:
                                formatted_stack.append(i)
                        message_log.send("You see " + ", ".join(formatted_stack) + ".")

                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

            if game_map.tiles[destination_x][destination_y].char == \
                    tilemap()["door_closed"]:
                message_log.send("The door is locked...")
                time_counter.take_turn(1)
                game_state = GameStates.ENEMY_TURN

        if key == blt.TK_PERIOD or key == blt.TK_KP_5:
            time_counter.take_turn(1)
            #player.spirit_power -= 1
            power_msg = "Spirit power left: " + \
                str(player.spirit_power)
            game_state = GameStates.ENEMY_TURN

        if key == blt.TK_CLOSE:
            break

        if key == blt.TK_ESCAPE:
            blt.clear()
            main()

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

        if player.spirit_power >= insights:
            insights += 10
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
            draw_ui(msg_panel, msg_panel_borders, screen_borders)
            fov_recompute = True

        if game_state == GameStates.ENEMY_TURN:

            for entity in entities:
                if entity.ai:
                    combat_msg = entity.ai_c.take_turn(
                        player, fov_map, game_map, entities, time_counter)
                    fov_recompute = True
                    if combat_msg:
                        message_log.send(combat_msg)
                        draw_stats(player, viewport_x, viewport_y, power_msg)
                    if player.fighter_c.dead:
                        kill_msg, game_state = kill_player(player)
                        message_log.send(kill_msg)
                        draw_stats(player, viewport_x, viewport_y, power_msg)
                        break
                if entity.fighter_c and entity.fighter_c.dead:
                    player.spirit_power += 11
                    player.fighter_c.hp += entity.fighter_c.power
                    message_log.send(kill_monster(entity))
                    message_log.send("I feel my power returning!")
                    power_msg = "Spirit power left: " + \
                        str(player.spirit_power)
            if not game_state == GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN

    blt.close()


if __name__ == '__main__':
    blt_init()
    main()
