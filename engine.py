from math import floor, ceil

from bearlibterminal import terminal as blt

from camera import Camera
from components.abilities import Abilities
from components.inventory import Inventory
from components.player import Player
from components.cursor import Cursor
from components.light_source import LightSource
from components.status_effects import StatusEffects
from data import json_data
from death_functions import kill_monster, kill_player
from draw import draw_all, draw_messages, draw_stats, draw_ui, clear_entities, draw_side_panel_content
from entity import Entity, blocking_entity
from fighter_stats import get_fighter_data
from game_states import GameStates
from helpers import get_article
from input_handlers import handle_keys
from map_objects.levels import level_change
from map_objects.tilemap import init_tiles, tilemap
from map_objects.minimap import test_dynamic_sprites
from random import randint
from ui.elements import UIElements, Panel
from ui.game_messages import MessageLog
from ui.menus import main_menu, character_menu
from ui.message_history import show_msg_history
import settings


def blt_init():
    blt.composition(True)

    blt.open()

    window_title = 'SpiritQuestRL'
    size = 'size=200x80'
    title = 'title=' + window_title
    cellsize = 'cellsize=auto'
    resizable = 'resizeable=false'
    window = "window: " + size + "," + title + "," + cellsize + "," + resizable

    blt.set(window)
    blt.set("font: default")
    init_tiles()


def new_game(choice, ui_elements):

    # Initialize game data
    game_data = json_data.JsonData()
    json_data.data = game_data
    # Create player
    inventory_component = Inventory(26)
    fighter_component = get_fighter_data("player")
    light_component = LightSource(radius=fighter_component.fov)
    player_component = Player(50)
    abilities_component = Abilities("player")
    status_effects_component = StatusEffects("player")
    player = Entity(
        1, 1, 3, player_component.char["player"], None, "player", blocks=True, player=player_component,
        fighter=fighter_component, inventory=inventory_component, light_source=light_component,
        abilities=abilities_component, status_effects=status_effects_component, stand_on_messages=False)
    player.player.avatar["player"] = fighter_component
    player.player.avatar[choice] = get_fighter_data(choice)
    player.player.avatar[choice].owner = player
    player.abilities.initialize_abilities(choice)
    player.player.char[choice] = tilemap()["monsters"][choice]
    player.player.char_exp[choice] = 20

    player.player.avatar[choice].max_hp += 20
    player.player.avatar[choice].hp += 20
    player.player.avatar[choice].power += 1

    blt.clear_area(2, settings.viewport_h +
                   settings.ui_offset_y + 1, ui_elements.viewport_x, 1)

    if settings.gfx == "ascii":
        player.char = tilemap()["player"]
        player.color = "lightest green"

    fov_recompute = True
    message_log = MessageLog(4)

    # Initialize game camera
    settings.camera_width = int(floor(settings.viewport_w / settings.ui_offset_x + 2))
    settings.camera_height = int(floor(settings.viewport_h / settings.ui_offset_y + 2))
    settings.camera_bound_x = ceil(settings.camera_offset)
    settings.camera_bound_y = ceil(settings.camera_offset)
    settings.camera_bound_x2 = settings.camera_width - ceil(settings.camera_offset)
    settings.camera_bound_y2 = settings.camera_height - ceil(settings.camera_offset)

    game_camera = Camera(1, 1, settings.camera_width, settings.camera_height)


    levels = {}
    time_counter = settings.TimeCounter()
    insights = 200
    game_state = GameStates.PLAYER_TURN

    return game_camera, game_state, player, levels, message_log, time_counter, insights, fov_recompute


def game_loop(main_menu_show=True, choice=None):
    ui_elements = UIElements()
    draw_ui(ui_elements)

    if main_menu_show:
        choice = main_menu(ui_elements=ui_elements)
        draw_ui(ui_elements)
    game_camera, game_state, player, levels, message_log, time_counter, \
        insights, fov_recompute = new_game(choice, ui_elements)

    game_map, entities, player = level_change(
        "hub", levels, player, ui_elements=ui_elements)

    #draw_ui(ui_elements)

    while True:
        if fov_recompute:
            player.light_source.recompute_fov(player.x, player.y)
            player.player.init_light()

        draw_all(game_map, game_camera, player, entities, ui_elements)
        draw_messages(ui_elements.msg_panel, message_log)

        fov_recompute = False
        blt.refresh()

        key = blt.read()
        #clear_entities(entities, game_camera)
        action = handle_keys(key)

        move = action.get('move')
        pickup = action.get('pickup')
        interact = action.get("interact")
        stairs = action.get('stairs')
        minimap = action.get('map')
        fullscreen = action.get('fullscreen')

        if not player.fighter.dead:
            player.status_effects.process_effects()

        if fullscreen:
            blt.set("window.fullscreen=true")

        if game_state == GameStates.PLAYER_DEAD:
            while True:
                key = blt.read()
                if key == blt.TK_CLOSE:
                    break

                if key == blt.TK_ESCAPE:
                    new_choice = main_menu(resume=False, ui_elements=ui_elements)
                    if not new_choice:
                        draw_ui(ui_elements)
                        fov_recompute = True
                    else:
                        blt.layer(1)
                        blt.clear_area(ui_elements.msg_panel.x * settings.ui_offset_x, ui_elements.msg_panel.y * settings.ui_offset_y,
                                       ui_elements.msg_panel.w *
                                       settings.ui_offset_x, ui_elements.msg_panel.h * settings.ui_offset_y)
                        blt.clear_area(settings.viewport_center_x - 5,
                                       settings.viewport_h + settings.ui_offset_y + 1, settings.viewport_w, 1)
                        game_loop(False, new_choice)

        if player.fighter.paralyzed:
            message_log.send("You are paralyzed!")
            time_counter.take_turn(1)
            game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.PLAYER_TURN:
            # Begin player turn
            # Non-turn taking UI functions

            if key == blt.TK_CLOSE:
                return False, False, None

            if key == blt.TK_ESCAPE:

                new_choice = main_menu(resume=True, ui_elements=ui_elements)
                if not new_choice:
                    draw_ui(ui_elements)
                    fov_recompute = True
                else:
                    message_log.clear()
                    draw_messages(ui_elements.msg_panel, message_log)
                    return True, False, new_choice

            if key == blt.TK_PERIOD or key == blt.TK_KP_5:
                time_counter.take_turn(1)
                # player.player.spirit_power -= 1
                message_log.send("You wait a turn.")
                settings.old_stack = settings.stack
                game_state = GameStates.ENEMY_TURN

            # Turn taking functions

            if move:

                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                # Handle player attack
                if not game_map.is_blocked(destination_x, destination_y):
                    target = blocking_entity(
                        entities, destination_x, destination_y)
                    if target:
                        combat_msg = player.fighter.attack(target, player.player.sel_attack)

                        message_log.send(combat_msg)
                        # player.player.spirit_power -= 0.5
                        time_counter.take_turn(1)
                        draw_stats(player, target)

                    else:
                        if player.fighter.mv_spd <= 0:
                            message_log.send("You are unable to move!")
                            time_counter.take_turn(1)
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

                settings.old_stack = settings.stack
                settings.stack = []

            elif interact:
                if "doors" in entities:
                    for entity in entities["doors"]:
                        if ((entity.x, entity.y) == (player.x - 1, player.y) or
                                (entity.x, entity.y) == (player.x - 1, player.y - 1) or
                                (entity.x, entity.y) == (player.x, player.y - 1) or
                                (entity.x, entity.y) == (player.x + 1, player.y - 1) or
                                (entity.x, entity.y) == (player.x + 1, player.y) or
                                (entity.x, entity.y) == (player.x + 1, player.y + 1) or
                                (entity.x, entity.y) == (player.x, player.y + 1) or
                                (entity.x, entity.y) == (player.x - 1, player.y + 1)):
                            if entity.door.status == "closed":
                                entity.door.set_status("open", game_map)
                                message_log.send("You open the door.")
                                time_counter.take_turn(1)
                                game_state = GameStates.ENEMY_TURN
                            elif entity.door.status == "open":
                                entity.door.set_status("closed", game_map)
                                message_log.send("You close the door.")
                                time_counter.take_turn(1)
                                game_state = GameStates.ENEMY_TURN
                            else:
                                message_log.send("The door is locked.")
                                time_counter.take_turn(1)
                                game_state = GameStates.ENEMY_TURN
                if "items" in entities:
                    for entity in entities["items"]:
                        if ((entity.x, entity.y) == (player.x - 1, player.y) or
                                (entity.x, entity.y) == (player.x - 1, player.y - 1) or
                                (entity.x, entity.y) == (player.x, player.y - 1) or
                                (entity.x, entity.y) == (player.x + 1, player.y - 1) or
                                (entity.x, entity.y) == (player.x + 1, player.y) or
                                (entity.x, entity.y) == (player.x + 1, player.y + 1) or
                                (entity.x, entity.y) == (player.x, player.y + 1) or
                                (entity.x, entity.y) == (player.x, player.y) or
                                (entity.x, entity.y) == (player.x - 1, player.y + 1)):

                            interact_msg = entity.item.interaction(game_map)
                            if interact_msg:
                                message_log.send(interact_msg)

            elif pickup:
                if "items" in entities:
                    for entity in entities["items"]:
                        if entity.x == player.x and entity.y == player.y and entity.item.pickable:
                            pickup_msg = player.inventory.add_item(entity)
                            message_log.send(pickup_msg)
                            for item in settings.stack:
                                if entity.name == item.split(" ", 1)[1]:
                                    settings.stack.remove(item)
                            game_map.tiles[entity.x][entity.y].entities_on_tile.remove(entity)
                            entities["items"].remove(entity)
                            time_counter.take_turn(1)
                            game_state = GameStates.ENEMY_TURN
                            break
                        # else:
                        #     message_log.send("There is nothing here to pick up.")
                else:
                    message_log.send("There is nothing here to pick up.")

            elif stairs:
                if "stairs" in entities:
                    for entity in entities["stairs"]:
                        if player.x == entity.x and player.y == entity.y:
                            game_map.tiles[player.x][player.y].entities_on_tile.remove(player)
                            game_map, entities, player = level_change(
                                entity.stairs.destination[0], levels, player, entities, game_map, entity.stairs, ui_elements=ui_elements)

                    settings.old_stack = settings.stack

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
                    draw_messages(ui_elements.msg_panel, message_log)
                    fov_recompute = True

            elif key == blt.TK_X:
                game_state = GameStates.TARGETING
                cursor_component = Cursor()
                cursor = Entity(player.x, player.y, 4, 0xE800 + 1746, "light yellow", "cursor",
                                cursor=cursor_component, stand_on_messages=False)
                game_map.tiles[cursor.x][cursor.y].entities_on_tile.append(cursor)
                entities["cursor"] = [cursor]

            if key == blt.TK_F1:
                character_menu(player)
                draw_ui(ui_elements)
                draw_side_panel_content(game_map, player, ui_elements)
                fov_recompute = True

            if key == blt.TK_M:
                show_msg_history(
                    message_log.history, "Message history")
                draw_ui(ui_elements)
                draw_side_panel_content(game_map, player, ui_elements)
                fov_recompute = True

            if key == blt.TK_A:
                game_state = GameStates.MENU


            if key == blt.TK_I:
                show_items = []
                for item in player.inventory.items:
                    show_items.append(get_article(item.name) + " " + item.name)
                show_msg_history(
                    show_items, "Inventory")
                draw_ui(ui_elements)
                draw_side_panel_content(game_map, player, ui_elements)
                fov_recompute = True

            if key == blt.TK_TAB:
                test_dynamic_sprites(game_map, ui_elements)
                draw_ui(ui_elements)
                fov_recompute = True

        elif game_state == GameStates.MENU:
            if key == blt.TK_A or key == blt.TK_ESCAPE:
                game_state = GameStates.PLAYER_TURN

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

                    settings.old_stack = settings.stack
                    settings.stack = []
                    if game_map.tiles[cursor.x][cursor.y].name is not None:
                        settings.stack.append(game_map.tiles[cursor.x][cursor.y].name.capitalize())

            elif key == blt.TK_ESCAPE or key == blt.TK_X:
                game_state = GameStates.PLAYER_TURN
                settings.old_stack = settings.stack
                settings.stack = []
                game_map.tiles[cursor.x][cursor.y].entities_on_tile.remove(cursor)
                del entities["cursor"]

            if player.fighter.paralyzed:
                message_log.send("You are paralyzed!")
                time_counter.take_turn(1)
                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            # Begin enemy turn
            fov_recompute = True
            draw_messages(ui_elements.msg_panel, message_log)

            for entity in entities["monsters"]:

                if entity.fighter:
                    entity.status_effects.process_effects()

                if player.fighter.dead:
                    kill_msg, game_state = kill_player(player)
                    message_log.send(kill_msg)
                    draw_stats(player)
                    break

                if entity.fighter and entity.fighter.dead:
                    level_up_msg = player.player.handle_player_exp(entity.fighter)
                    message_log.send(kill_monster(entity))
                    message_log.send("I feel my power returning!")
                    if level_up_msg:
                        message_log.send(level_up_msg)

                elif entity.fighter and entity.fighter.paralyzed:
                    message_log.send("The monster is paralyzed!")
                    game_state = GameStates.PLAYER_TURN

                elif entity.ai:
                    prev_pos_x, prev_pos_y = entity.x, entity.y
                    combat_msg = entity.ai.take_turn(
                        player, game_map, entities, time_counter)
                    game_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(entity)
                    game_map.tiles[entity.x][entity.y].entities_on_tile.append(entity)
                    if entity.occupied_tiles is not None:
                        game_map.tiles[prev_pos_x][prev_pos_y + 1].entities_on_tile.remove(entity)
                        game_map.tiles[prev_pos_x + 1][prev_pos_y + 1].entities_on_tile.remove(entity)
                        game_map.tiles[prev_pos_x + 1][prev_pos_y].entities_on_tile.remove(entity)

                        game_map.tiles[entity.x][entity.y + 1].entities_on_tile.append(entity)
                        game_map.tiles[entity.x + 1][entity.y + 1].entities_on_tile.append(entity)
                        game_map.tiles[entity.x + 1][entity.y].entities_on_tile.append(entity)

                    fov_recompute = True
                    if combat_msg:
                        message_log.send(combat_msg)
                        draw_stats(player)
                    if player.fighter.dead:
                        kill_msg, game_state = kill_player(player)
                        message_log.send(kill_msg)
                        draw_stats(player)
                        break
                    # Functions on monster death
                    if entity.fighter and entity.fighter.dead:
                        level_up_msg = player.player.handle_player_exp(entity.fighter)
                        message_log.send(kill_monster(entity))
                        message_log.send("I feel my power returning!")
                        if level_up_msg:
                            message_log.send(level_up_msg)

            if not game_state == GameStates.PLAYER_DEAD:
                game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    blt_init()
    restart = True
    avatar = None
    menu_show = True
    while restart:
        restart, menu_show, avatar = game_loop(main_menu_show=menu_show, choice=avatar)
    blt.close()

