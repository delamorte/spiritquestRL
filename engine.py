from math import floor

from bearlibterminal import terminal as blt

from camera import Camera
from components.inventory import Inventory
from components.player import Player
from components.cursor import Cursor
from death_functions import kill_monster, kill_player
from draw import draw_all, draw_messages, draw_stats, draw_ui, clear_entities, draw_indicator
from entity import Entity, blocking_entity
from fighter_stats import get_fighter_stats
from fov import recompute_fov
from game_states import GameStates
from helpers import get_article
from input_handlers import handle_keys
from map_objects.levels import level_change
from map_objects.tilemap import init_tiles, tilemap
from map_objects.minimap import test_dynamic_sprites
from random import randint
from ui.elements import init_ui
from ui.game_messages import MessageLog
from ui.menus import main_menu
from ui.message_history import show_msg_history
import variables

"""
TODO:

- Add abilities on player and give them action cost
- Add stealth
- Items and inventory
- Npcs
- Minimap 
- UI elements for displaying current game map name
  and status effects
- Level up system
- Saving and loading
- Generate levels with a seed

FIX:

- Text alignment when resizing window

BUGS:

- Enemy HP not updated properly on death
- Sometimes floor gets drawn over wall in home


"""


def blt_init():
    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=150x60'
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
        1, 1, 3, player_component.char["player"], None, "player", blocks=True, player=player_component,
        fighter=fighter_component, inventory=inventory_component, stand_on_messages=False)
    player.player.avatar["player"] = fighter_component
    player.player.avatar[choice] = get_fighter_stats(choice)
    player.player.avatar[choice].owner = player
    player.player.char[choice] = tilemap()["monsters"][choice]

    player.player.avatar[choice].max_hp += 20
    player.player.avatar[choice].hp += 20
    player.player.avatar[choice].power += 1

    blt.clear_area(2, variables.viewport_y +
                   variables.ui_offset_y + 1, variables.viewport_x, 1)

    if variables.gfx == "ascii":
        player.char = tilemap()["player"]
        player.color = "lightest green"

    fov_recompute = True
    message_log = MessageLog(4)

    # Initialize game camera
    variables.camera_width = int(floor(blt.state(blt.TK_WIDTH) / variables.ui_offset_x) * variables.camera_offset)
    variables.camera_height = int(
        floor(blt.state(blt.TK_HEIGHT) / variables.ui_offset_y - 5) * variables.camera_offset)
    game_camera = Camera(1, 1, variables.camera_width, variables.camera_height)

    levels = {}
    time_counter = variables.TimeCounter()
    insights = 100
    game_state = GameStates.PLAYER_TURN

    return game_camera, game_state, player, levels, message_log, time_counter, insights, fov_recompute


def game_loop(main_menu_show=True, choice=None):
    msg_panel, msg_panel_borders, screen_borders = init_ui()
    draw_ui(msg_panel, msg_panel_borders, screen_borders)

    if main_menu_show:
        choice = main_menu()
        msg_panel, msg_panel_borders, screen_borders = init_ui()
        draw_ui(msg_panel, msg_panel_borders, screen_borders)
    game_camera, game_state, player, levels, message_log, time_counter, insights, fov_recompute = new_game(choice)

    game_map, entities, player, fov_map = level_change(
        "hub", levels, player)

    draw_ui(msg_panel, msg_panel_borders, screen_borders)

    while True:
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, player.fighter.fov, True, 0)

        draw_all(game_map, game_camera, player, entities, fov_map, msg_panel, msg_panel_borders, screen_borders)
        draw_messages(msg_panel, message_log)

        fov_recompute = False
        blt.refresh()

        key = blt.read()
        clear_entities(entities, game_camera)
        action = handle_keys(key)

        move = action.get('move')
        pickup = action.get('pickup')
        stairs = action.get('stairs')
        fullscreen = action.get('fullscreen')

        if not player.fighter.dead:
            effect_msg, game_state = player.fighter.process_effects(time_counter, game_state)

        message_log.send(effect_msg)

        if fullscreen:
            blt.set("window.fullscreen=true")

        if game_state == GameStates.PLAYER_DEAD:
            while True:
                key = blt.read()
                if key == blt.TK_CLOSE:
                    break

                if key == blt.TK_ESCAPE:
                    new_choice = main_menu(resume=False)
                    if not new_choice:
                        draw_ui(msg_panel, msg_panel_borders, screen_borders)
                        fov_recompute = True
                    else:
                        blt.layer(1)
                        blt.clear_area(msg_panel.x * variables.ui_offset_x, msg_panel.y * variables.ui_offset_y,
                                       msg_panel.w *
                                       variables.ui_offset_x, msg_panel.h * variables.ui_offset_y)
                        blt.clear_area(int(variables.viewport_x / 2) - 5,
                                       variables.viewport_y + variables.ui_offset_y + 1, variables.viewport_x, 1)
                        game_loop(False, new_choice)

        if game_state == GameStates.PLAYER_TURN:

            if key == blt.TK_CLOSE:
                break

            if key == blt.TK_ESCAPE:

                new_choice = main_menu(resume=True)
                if not new_choice:
                    draw_ui(msg_panel, msg_panel_borders, screen_borders)
                    fov_recompute = True
                else:
                    return True, False, new_choice

            if move:

                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                # Handle player attack
                if not game_map.is_blocked(destination_x, destination_y):
                    target = blocking_entity(
                        entities, destination_x, destination_y)
                    if target:
                        if len(player.fighter.abilities) > 0 and randint(1, 100) < player.fighter.abilities[0][1]:
                            combat_msg = player.fighter.attack(target, player.fighter.abilities[0][0])
                        else:
                            combat_msg = player.fighter.attack(target)

                        message_log.send(combat_msg)
                        # player.player.spirit_power -= 0.5
                        time_counter.take_turn(1)
                        draw_stats(player, target)

                    else:
                        prev_pos_x, prev_pos_y = player.x, player.y
                        player.move(dx, dy)
                        time_counter.take_turn(1 / player.fighter.mv_spd)
                        fov_recompute = True
                        game_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(player)
                        game_map.tiles[player.x][player.y].entities_on_tile.append(player)

                    game_state = GameStates.ENEMY_TURN

                else:
                    if "doors" in entities:
                        for entity in entities["doors"]:
                            if destination_x == entity.x and destination_y == entity.y and entity.door.status == "locked":
                                message_log.send("The door is locked...")
                                time_counter.take_turn(1)
                                game_state = GameStates.ENEMY_TURN
                            elif destination_x == entity.x and destination_y == entity.y and entity.door.status == "closed":
                                entity.door.set_status("open", game_map)
                                message_log.send("You open the door.")
                                time_counter.take_turn(1)
                                game_state = GameStates.ENEMY_TURN

                variables.old_stack = variables.stack
                variables.stack = []

            elif pickup:
                for entity in entities["items"]:
                    if entity.x == player.x and entity.y == player.y and entity.item.pickable:
                        pickup_msg = player.inventory.add_item(entity)
                        message_log.send(pickup_msg)
                        for item in variables.stack:
                            if entity.name == item.split(" ", 1)[1]:
                                variables.stack.remove(item)
                        game_map.tiles[entity.x][entity.y].entities_on_tile.remove(entity)
                        entities["items"].remove(entity)
                        time_counter.take_turn(1)
                        game_state = GameStates.ENEMY_TURN
                        break
                else:
                    message_log.send("There is nothing here to pick up.")

            elif key == blt.TK_PERIOD or key == blt.TK_KP_5:
                time_counter.take_turn(1)
                # player.player.spirit_power -= 1
                message_log.send("You wait a turn.")
                variables.old_stack = variables.stack
                game_state = GameStates.ENEMY_TURN

            elif key == blt.TK_X:
                game_state = GameStates.TARGETING
                cursor_component = Cursor()
                cursor = Entity(player.x, player.y, 4, 0xE700 + 1746, "light yellow", "cursor",
                                cursor=cursor_component, stand_on_messages=False)
                game_map.tiles[cursor.x][cursor.y].entities_on_tile.append(cursor)
                entities["cursor"] = [cursor]

            elif player.player.spirit_power <= 0:
                game_map, entities, player, fov_map = level_change(
                    "hub", levels, player, entities, game_map, fov_map)
                message_log.clear()
                message_log.send("I have no power to meditate longer..")
                player.player.spirit_power = 50
                player.fighter.hp = player.fighter.max_hp

            elif stairs:

                for entity in entities["stairs"]:
                    if player.x == entity.x and player.y == entity.y:
                        game_map.tiles[player.x][player.y].entities_on_tile.remove(player)
                        game_map, entities, player, fov_map = level_change(
                            entity.stairs.destination[0], levels, player, entities, game_map, fov_map, entity.stairs)

                variables.old_stack = variables.stack

                if game_map.name == "cavern" and game_map.dungeon_level == 1:
                    message_log.clear()
                    message_log.send(
                        "A sense of impending doom fills you as you delve into the cavern.")
                    message_log.send("RIBBIT!")

                elif game_map.name == "dream":
                    message_log.clear()
                    message_log.send(
                        "I'm dreaming... I feel my spirit power draining.")
                    message_log.send("I'm hungry..")
                draw_messages(msg_panel, message_log)
                fov_recompute = True

            elif key == blt.TK_M:
                show_msg_history(
                    message_log.history, "Message history")
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
                fov_recompute = True

            elif key == blt.TK_I:
                show_items = []
                for item in player.inventory.items:
                    show_items.append(get_article(item.name) + " " + item.name)
                show_msg_history(
                    show_items, "Inventory")
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
                fov_recompute = True

            elif key == blt.TK_TAB:
                test_dynamic_sprites(game_map)
                draw_ui(msg_panel, msg_panel_borders, screen_borders)
                fov_recompute = True

        elif game_state == GameStates.TARGETING:

            if move:
                dx, dy = move
                destination_x = cursor.x + dx
                destination_y = cursor.y + dy
                x, y = game_camera.get_coordinates(destination_x, destination_y)

                if 0 < x < game_camera.width - 1 and 0 < y < game_camera.height - 1:
                    prev_pos_x, prev_pos_y = cursor.x, cursor.y
                    cursor.move(dx, dy)
                    game_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(cursor)
                    game_map.tiles[cursor.x][cursor.y].entities_on_tile.append(cursor)
                    fov_recompute = True
                    variables.old_stack = variables.stack
                    variables.stack = []

            elif key == blt.TK_ESCAPE or key == blt.TK_X:
                game_state = GameStates.PLAYER_TURN
                variables.old_stack = variables.stack
                variables.stack = []
                game_map.tiles[cursor.x][cursor.y].entities_on_tile.remove(cursor)
                del entities["cursor"]

        if game_state == GameStates.ENEMY_TURN:
            if player.player.spirit_power >= insights:
                insights += 10
                message_log.clear()
                message_log.send("My spirit has granted me new insights!")
                message_log.send("I should explore around my home..")
                game_map, entities, player, fov_map = level_change(
                    "hub", levels, player, entities, game_map, fov_map)
                # Currently opens the door in hub
                for entity in entities["doors"]:
                    if entity.door.name == "d_entrance":
                        entity.door.set_status("open", game_map)

            draw_messages(msg_panel, message_log)

            for entity in entities["monsters"]:

                if entity.fighter:
                    effect_msg, game_state = entity.fighter.process_effects(time_counter, game_state)
                    message_log.send(effect_msg)

                if player.fighter.dead:
                    kill_msg, game_state = kill_player(player)
                    message_log.send(kill_msg)
                    draw_stats(player)
                    break
                if entity.ai:
                    prev_pos_x, prev_pos_y = entity.x, entity.y
                    combat_msg = entity.ai.take_turn(
                        player, fov_map, game_map, entities, time_counter)
                    game_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(entity)
                    game_map.tiles[entity.x][entity.y].entities_on_tile.append(entity)
                    fov_recompute = True
                    if combat_msg:
                        message_log.send(combat_msg)
                        draw_stats(player)
                    if player.fighter.dead:
                        kill_msg, game_state = kill_player(player)
                        message_log.send(kill_msg)
                        draw_stats(player)
                        break
                    if entity.fighter and entity.fighter.dead:
                        player.player.spirit_power += entity.fighter.max_hp
                        player.fighter.hp += entity.fighter.power
                        message_log.send(kill_monster(entity))
                        message_log.send("I feel my power returning!")

            if not game_state == GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN

    blt.close()


if __name__ == '__main__':
    blt_init()
    restart = True
    avatar = None
    menu_show = True
    while restart:
        restart, menu_show, avatar = game_loop(main_menu_show=menu_show, choice=avatar)

