from collections import Counter
from math import floor

from bearlibterminal import terminal as blt

from camera import Camera
from components.inventory import Inventory
from components.player import Player
from death_functions import kill_monster, kill_player
from draw import draw_all, draw_stats, draw_ui, clear_entities
from entity import Entity, blocking_entity
from fighter_stats import get_fighter_stats
from fov import recompute_fov
from game_states import GameStates
from helpers import get_article
from input_handlers import handle_keys
from map_objects.levels import level_change
from map_objects.tilemap import init_tiles, tilemap
from ui.elements import init_ui
from ui.game_messages import MessageLog
from ui.menus import main_menu
from ui.message_history import show_msg_history
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

def new_game(choice):
    
    # Create player
    
    inventory_component = Inventory(26)
    fighter_component = get_fighter_stats("player")
    player_component = Player(50)
    player = Entity(
        1, 1, 12, player_component.char["player"], None, "player", blocks=True, player=player_component, fighter=fighter_component, inventory=inventory_component)
    player.player.avatar["player"] = fighter_component
    player.player.avatar[choice] = get_fighter_stats(choice)
    player.player.avatar[choice].owner = player
    player.player.char[choice] = tilemap()["monsters"][choice]
    
    player.player.avatar[choice].max_hp += 10
    player.player.avatar[choice].hp += 10
    player.player.avatar[choice].power += 1
    
    if variables.gfx is "ascii":
        player.char = tilemap()["player"]
        player.color = "lightest green"
    
    fov_recompute = True
    message_log = MessageLog(5)
    # Initialize game camera
    game_camera = Camera(1, 1, int(floor(blt.state(blt.TK_WIDTH) / variables.ui_offset_x) * variables.camera_offset),
                         int(floor(blt.state(blt.TK_HEIGHT) / variables.ui_offset_y - 5) * variables.camera_offset))
    levels = []
    power_msg = "Spirit power left: " + str(player.player.spirit_power)
    time_counter = variables.TimeCounter()
    insights = 600
    game_state = GameStates.PLAYER_TURN
    
    return game_camera, game_state, player, levels, message_log, time_counter, insights, power_msg, fov_recompute
    
def game_loop(main_menu_show=True, choice=None):
    
    msg_panel, msg_panel_borders, screen_borders = init_ui()
    draw_ui(msg_panel, msg_panel_borders, screen_borders)
    
    if main_menu_show:
        choice = main_menu()
    game_camera, game_state, player, levels, message_log, time_counter, insights, power_msg, fov_recompute = new_game(choice)

    game_map, entities, player, fov_map = level_change(
    "hub", levels, player)

    key = None
    while True:
        print(str(time_counter.turn))
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, player.fighter.fov, True, 0)

        draw_all(game_map, game_camera, entities, player, player.x, player.y,
                 fov_map, fov_recompute, message_log, msg_panel, power_msg)

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
                    draw_stats(player, power_msg, target)

                else:
                    player.move(dx, dy)

                    time_counter.take_turn(1 / player.fighter.mv_spd)

                    if (game_map.name is not "hub" and
                            game_map.name is not "debug"):
                        #player.player.spirit_power -= 0.5
                        power_msg = "Spirit power left: " + \
                            str(player.player.spirit_power)
                        draw_stats(player, power_msg)

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

            new_choice = main_menu(resume=True)
            if not new_choice:
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
                fov_recompute = True
            else:
                game_loop(False, new_choice)

        if fullscreen:
            blt.set("window.fullscreen=true")

        if player.player.spirit_power <= 0:
            game_map, entities, player, fov_map = level_change(
                "hub", levels, player, game_map, entities, fov_map)
            message_log.clear()
            message_log.send("I have no power to meditate longer..")
            player.player.spirit_power = 50
            player.fighter.hp = player.fighter.max_hp
            power_msg = "Spirit power left: " + \
                str(player.player.spirit_power)

        if player.player.spirit_power >= insights:
            insights += 10
            message_log.send("My spirit has granted me new insights!")
            game_map, entities, player, fov_map = level_change(
                "hub", levels, player, game_map, entities, fov_map)

            # Currently opens the door in hub
            for y in range(game_map.height):
                for x in range(game_map.width):
                    if game_map.tiles[x][y].char[1] == tilemap()["door_closed"]:
                        game_map.tiles[x][y].char[1] = tilemap()["door_open"]
                        game_map.tiles[x][y].blocked = False

        if stairs:
            if game_map.tiles[player.x][player.y].char[1] == tilemap()["campfire"]:
                game_map, entities, player, fov_map = level_change(
                    "dream", levels, player, game_map, entities, fov_map)
                message_log.clear()
                message_log.send(
                    "I'm dreaming... I feel my spirit power draining.")
                message_log.send("I'm hungry..")
                fov_recompute = True

        if key == blt.TK_M:
            show_msg_history(
                message_log.history, "Message history")
            draw_ui(msg_panel, msg_panel_borders, screen_borders)
            fov_recompute = True

        if key == blt.TK_I:
            show_items = []
            for item in player.inventory.items:
                show_items.append(get_article(item.name) + " " + item.name)
            show_msg_history(
                show_items, "Inventory")
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
                        draw_stats(player, power_msg)
                    if player.fighter.dead:
                        kill_msg, game_state = kill_player(player)
                        message_log.send(kill_msg)
                        draw_stats(player, power_msg)
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
    game_loop()
