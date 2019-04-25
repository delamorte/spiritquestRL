from bearlibterminal import terminal as blt
from camera import Camera
from collections import Counter
from death_functions import kill_monster, kill_player
from draw import draw_all, draw_stats, draw_ui, clear_entities
from entity import blocking_entity
from game_states import GameStates
from fov import initialize_fov, recompute_fov
from helpers import get_article
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from math import floor
from map_objects.tilemap import init_tiles, tilemap
from ui.elements import init_ui
from ui.game_messages import MessageLog
from ui.message_history import show_msg_history
from ui.menus import main_menu, choose_avatar
import variables

"""
TODO:

- Improve combat mechanics
- Abilities and status effects
- Items and inventory
- Npcs
- Minimap
- Saving and loading
- Examine/view mode
- Generate levels with a seed

"""


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
    init_tiles()


def level_init(game_map, player):

    # Initialize entities
    entities = []
    player, entities = game_map.place_entities(player, entities)

    # Initialize game camera
    game_camera = Camera(1, 1, int(floor(blt.state(blt.TK_WIDTH) / variables.ui_offset_x) * variables.camera_offset),
                         int(floor(blt.state(blt.TK_HEIGHT) / variables.ui_offset_y - 5) * variables.camera_offset))
    # Initialize field of view
    fov_map = initialize_fov(game_map)

    return game_map, game_camera, entities, player, fov_map


def level_change(level_name, levels, player):

    if not levels:
        game_map = GameMap(50, 50, "hub")
        game_map.generate_hub()
        levels.append(game_map)

    if level_name is "hub":
        for level in levels:
            if level.name is level_name:
                game_map = level
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)
        player.fighter = player.player.avatar["player"]
        player.char = player.player.char["player"]

    if level_name is "dream":
        choice = choose_avatar(player)
        game_map = GameMap(100, 100, "dream")
        game_map.generate_forest()
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)
        player.fighter = player.player.avatar[choice]
        player.char = player.player.char[choice]

    # Set debug level
    if level_name is "debug":
        game_map = GameMap(100, 100, "debug")
        # game_map.generate_trees(0, 0, game_map.width,
        #                        game_map.height, 20, block_sight=True)
        # game_map.generate_forest()
        game_map, game_camera, entities, player, fov_map = level_init(
            game_map, player)

    return game_map, game_camera, entities, player, fov_map


def main():

    fov_recompute = True
    viewport_x, viewport_y, msg_panel, msg_panel_borders, screen_borders = init_ui()
    draw_ui(msg_panel, msg_panel_borders, screen_borders)
    message_log = MessageLog(5)
    player, viewport_x, viewport_y, msg_panel = main_menu(
        viewport_x, viewport_y, msg_panel)
    levels = []
    game_map, game_camera, entities, player, fov_map = level_change(
        "hub", levels, player)
    power_msg = "Spirit power left: " + str(player.player.spirit_power)
    time_counter = variables.TimeCounter()
    insights = 600
    game_state = GameStates.PLAYER_TURN
    key = None
    while True:
        print(str(time_counter.turn))
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, player.fighter.fov, True, 0)

        draw_all(game_map, game_camera, entities, player, player.x, player.y,
                 fov_map, fov_recompute, message_log, msg_panel, power_msg,
                 viewport_x, viewport_y)

        fov_recompute = False
        blt.refresh()

        key = blt.read()
        clear_entities(entities, game_camera)
        action = handle_keys(key)

        move = action.get('move')
        pickup = action.get('pickup')
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
                    combat_msg = player.fighter.attack(target)
                    message_log.send(combat_msg)
                    player.player.spirit_power -= 0.5
                    time_counter.take_turn(1)
                    draw_stats(player, viewport_x,
                               viewport_y, power_msg, target)

                else:
                    player.move(dx, dy)

                    time_counter.take_turn(1 / player.fighter.mv_spd)

                    if (game_map.name is not "hub" and
                            game_map.name is not "debug"):
                        #player.player.spirit_power -= 0.5
                        power_msg = "Spirit power left: " + \
                            str(player.player.spirit_power)
                        draw_stats(player, viewport_x, viewport_y, power_msg)

                    if game_map.tiles[player.x][player.y].char[1] == tilemap()["campfire"]:
                        message_log.send(
                            "Meditate and go to dream world with '<' or '>'")

                    # If there are entities under the player, print them
                    stack = []
                    for entity in entities:
                        if not entity.fighter:
                            if player.x == entity.x and player.y == entity.y:
                                if entity.item:
                                    stack.append(get_article(
                                        entity.name) + " " + entity.name)
                                else:
                                    stack.append(entity.name)

                    if len(stack) > 0:
                        d = dict(Counter(stack))
                        formatted_stack = []
                        for i in d:
                            if d[i] > 1:
                                formatted_stack.append(i + " x" + str(d[i]))
                            else:
                                formatted_stack.append(i)
                        message_log.send(
                            "You see " + ", ".join(formatted_stack) + ".")

                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

            if game_map.tiles[destination_x][destination_y].char[1] == \
                    tilemap()["door_closed"]:
                message_log.send("The door is locked...")
                time_counter.take_turn(1)
                game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_msg = player.inventory.add_item(entity)
                    message_log.send(pickup_msg)
                    entities.remove(entity)
                    time_counter.take_turn(1)
                    game_state = GameStates.ENEMY_TURN
                    break
            else:
                message_log.send("There is nothing here to pick up.")

        if key == blt.TK_PERIOD or key == blt.TK_KP_5:
            time_counter.take_turn(1)
            #player.player.spirit_power -= 1
            power_msg = "Spirit power left: " + \
                str(player.player.spirit_power)
            game_state = GameStates.ENEMY_TURN

        if key == blt.TK_CLOSE:
            break

        if key == blt.TK_ESCAPE:
            blt.clear()
            main()

        if fullscreen:
            blt.set("window.fullscreen=true")

        if player.player.spirit_power <= 0:
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels, player)
            message_log.clear()
            message_log.send("I have no power to meditate longer..")
            player.player.spirit_power = 50
            player.fighter.hp = player.fighter.max_hp
            power_msg = "Spirit power left: " + \
                str(player.player.spirit_power)

        if player.player.spirit_power >= insights:
            insights += 10
            message_log.send("My spirit has granted me new insights!")
            game_map, game_camera, entities, player, fov_map = level_change(
                "hub", levels, player)

            # Currently opens the door in hub
            for y in range(game_map.height):
                for x in range(game_map.width):
                    if game_map.tiles[x][y].char[1] == tilemap()["door_closed"]:
                        game_map.tiles[x][y].char[1] = tilemap()["door_open"]
                        game_map.tiles[x][y].blocked = False

        if stairs:
            if game_map.tiles[player.x][player.y].char[1] == tilemap()["campfire"]:
                game_map, game_camera, entities, player, fov_map = level_change(
                    "dream", levels, player)
                message_log.clear()
                message_log.send(
                    "I'm dreaming... I feel my spirit power draining.")
                message_log.send("I'm hungry..")
                fov_recompute = True

        if key == blt.TK_M:
            show_msg_history(
                message_log.history, viewport_x, viewport_y, "Message history")
            draw_ui(msg_panel, msg_panel_borders, screen_borders)
            fov_recompute = True

        if key == blt.TK_I:
            show_items = []
            for item in player.inventory.items:
                show_items.append(get_article(item.name) + " " + item.name)
            show_msg_history(
                show_items, viewport_x, viewport_y, "Inventory")
            draw_ui(msg_panel, msg_panel_borders, screen_borders)
            fov_recompute = True

        if game_state == GameStates.ENEMY_TURN:

            for entity in entities:
                if entity.ai:
                    combat_msg = entity.ai.take_turn(
                        player, fov_map, game_map, entities, time_counter)
                    fov_recompute = True
                    if combat_msg:
                        message_log.send(combat_msg)
                        draw_stats(player, viewport_x, viewport_y, power_msg)
                    if player.fighter.dead:
                        kill_msg, game_state = kill_player(player)
                        message_log.send(kill_msg)
                        draw_stats(player, viewport_x, viewport_y, power_msg)
                        break
                if entity.fighter and entity.fighter.dead:
                    player.player.spirit_power += 11
                    player.fighter.hp += entity.fighter.power
                    message_log.send(kill_monster(entity))
                    message_log.send("I feel my power returning!")
                    power_msg = "Spirit power left: " + \
                        str(player.player.spirit_power)
            if not game_state == GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN

    blt.close()


if __name__ == '__main__':
    blt_init()
    main()
