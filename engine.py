from bearlibterminal import terminal as blt

from camera import Camera
from components.abilities import Abilities
from components.inventory import Inventory
from components.menus.main_menu import MainMenu
from components.player import Player
from components.cursor import Cursor
from components.light_source import LightSource
from components.status_effects import StatusEffects
from data import json_data
from death_functions import kill_monster, kill_player
from render_functions import RenderFunctions
from components.entity import Entity, blocking_entity
from fighter_stats import get_fighter_data
from game_states import GameStates
from helpers import get_article
from input_handlers import handle_keys
from map_objects.levels import Levels
from map_objects.tilemap import init_tiles, tilemap
from map_objects.show_map import test_dynamic_sprites
from ui.elements import UIElements
from ui.game_messages import MessageLog
from ui.menus import Menus, MenuData
from ui.message_history import show_msg_history


class Engine:
    def __init__(self):
        self.render_functions = None
        self.cursor = None
        self.fov_recompute = None
        self.game_state = None
        self.time_counter = None
        self.game_camera = None
        self.message_log = None
        self.ui = None
        self.menus = None
        self.levels = None
        self.player = None

    def initialize(self):
        # Initialize game data from external files
        game_data = json_data.JsonData()
        json_data.data = game_data

        window_title = 'SpiritQuestRL'
        size = 'size=200x80'
        title = 'title=' + window_title
        cellsize = 'cellsize=auto'
        resizable = 'resizeable=true'
        window = "window: " + size + "," + title + "," + cellsize + "," + resizable

        blt.composition(True)
        blt.open()
        blt.set(window)
        blt.set("font: default")
        blt.set("input: filter=[keyboard]")

        # Needed to avoid insta-close and flush the input queue
        blt.refresh()
        blt.read()

        # Load tiles
        init_tiles()

        # Init UI
        self.ui = UIElements()
        self.ui.owner = self

        self.render_functions = RenderFunctions(self.ui.ui_offset_x, self.ui.ui_offset_y)
        self.render_functions.owner = self
        self.ui.render_functions = self.render_functions
        self.ui.draw()

        # Call main menu and start game loop
        main_menu_component = MainMenu(title_screen=True)
        self.menus = Menus(main_menu=main_menu_component)
        self.menus.owner = self

        self.menus.main_menu.show()

        self.menus.main_menu.title_screen = False
        self.game_loop()

    def init_new_game(self, params):
        choice = params
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
        player.player.insights = 200
        
        self.player = player

        character_menu = MenuData(name="avatar_info", params=self.player)
        self.menus.create_or_show_menu(character_menu)

        message_log = MessageLog(4)
        self.message_log = message_log
        self.message_log.owner = self

        # Initialize game camera
        game_camera = Camera(1, 1, self.ui.viewport.w, self.ui.viewport.h, self.ui.ui_offset_x, self.ui.ui_offset_y)
        self.game_camera = game_camera
        self.game_camera.owner = self

        levels = Levels()
        self.levels = levels
        self.levels.owner = self

        self.time_counter = self.TimeCounter()

        blt.clear_area(2, self.ui.viewport.offset_h +
                       self.ui.ui_offset_y + 1, self.ui.viewport.x, 1)

        # if settings.gfx == "ascii":
        #     player.char = tilemap()["player"]
        #     player.color = "lightest green"

        self.levels.change("hub")
        self.fov_recompute = True
        self.game_state = GameStates.PLAYER_TURN

    def game_loop(self):

        game_quit = False
        self.ui.draw()

        while not game_quit:
            if self.fov_recompute:
                self.player.light_source.recompute_fov(self.player.x, self.player.y)
                self.player.player.init_light()

            self.render_functions.draw_all()
            self.render_functions.draw_messages()

            self.fov_recompute = False
            blt.refresh()

            key = blt.read()

            action = handle_keys(key)

            move = action.get('move')
            pickup = action.get('pickup')
            interact = action.get("interact")
            stairs = action.get('stairs')
            minimap = action.get('map')
            fullscreen = action.get('fullscreen')

            if not self.player.fighter.dead:
                self.player.status_effects.process_effects()

            if fullscreen:
                blt.set("window.fullscreen=true")

            if self.game_state == GameStates.PLAYER_DEAD:
                while True:
                    key = blt.read()
                    if key == blt.TK_CLOSE:
                        break

                    if key == blt.TK_ESCAPE:
                        self.menus.main_menu.show()
                        self.ui.draw()
                        self.fov_recompute = True

            if self.player.fighter.paralyzed:
                self.message_log.send("You are paralyzed!")
                self.time_counter.take_turn(1)
                self.game_state = GameStates.ENEMY_TURN

            if self.game_state == GameStates.PLAYER_TURN:
                # Begin player turn
                # Non-turn taking UI functions

                if key == blt.TK_CLOSE:
                    return False

                if key == blt.TK_ESCAPE:
                    self.menus.main_menu.show()
                    self.ui.draw()
                    self.fov_recompute = True

                if key == blt.TK_PERIOD or key == blt.TK_KP_5:
                    self.time_counter.take_turn(1)
                    # player.player.spirit_power -= 1
                    self.message_log.send("You wait a turn.")
                    self.message_log.old_stack = self.message_log.stack
                    self.game_state = GameStates.ENEMY_TURN

                # Turn taking functions

                if move:

                    dx, dy = move
                    destination_x = self.player.x + dx
                    destination_y = self.player.y + dy

                    # Handle player attack
                    if not self.levels.current_map.is_blocked(destination_x, destination_y):
                        target = blocking_entity(
                            self.levels.current_map.entities, destination_x, destination_y)
                        if target:
                            combat_msg = self.player.fighter.attack(target, self.player.player.sel_weapon)

                            self.message_log.send(combat_msg)
                            # player.player.spirit_power -= 0.5
                            self.time_counter.take_turn(1)
                            self.render_functions.draw_stats(target)

                        else:
                            if self.player.fighter.mv_spd <= 0:
                                self.message_log.send("You are unable to move!")
                                self.time_counter.take_turn(1)
                            else:
                                prev_pos_x, prev_pos_y = self.player.x, self.player.y
                                self.player.move(dx, dy)
                                self.time_counter.take_turn(1 / self.player.fighter.mv_spd)
                                self.fov_recompute = True
                                self.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(self.player)
                                self.levels.current_map.tiles[self.player.x][self.player.y].entities_on_tile.append(self.player)

                        self.game_state = GameStates.ENEMY_TURN

                    else:
                        if "doors" in self.levels.current_map.entities:
                            for entity in self.levels.current_map.entities["doors"]:
                                if destination_x == entity.x and destination_y == entity.y and entity.door.status == "locked":
                                    self.message_log.send("The door is locked...")
                                    self.time_counter.take_turn(1)
                                    self.game_state = GameStates.ENEMY_TURN
                                elif destination_x == entity.x and destination_y == entity.y and entity.door.status == "closed":
                                    entity.door.set_status("open", self.levels.current_map)
                                    self.message_log.send("You open the door.")
                                    self.time_counter.take_turn(1)
                                    self.game_state = GameStates.ENEMY_TURN

                    self.message_log.old_stack = self.message_log.stack
                    self.message_log.stack = []

                elif interact:
                    if "doors" in self.levels.current_map.entities:
                        for entity in self.levels.current_map.entities["doors"]:
                            if ((entity.x, entity.y) == (self.player.x - 1, self.player.y) or
                                    (entity.x, entity.y) == (self.player.x - 1, self.player.y - 1) or
                                    (entity.x, entity.y) == (self.player.x, self.player.y - 1) or
                                    (entity.x, entity.y) == (self.player.x + 1, self.player.y - 1) or
                                    (entity.x, entity.y) == (self.player.x + 1, self.player.y) or
                                    (entity.x, entity.y) == (self.player.x + 1, self.player.y + 1) or
                                    (entity.x, entity.y) == (self.player.x, self.player.y + 1) or
                                    (entity.x, entity.y) == (self.player.x - 1, self.player.y + 1)):
                                if entity.door.status == "closed":
                                    entity.door.set_status("open", self.levels.current_map)
                                    self.message_log.send("You open the door.")
                                    self.time_counter.take_turn(1)
                                    self.game_state = GameStates.ENEMY_TURN
                                elif entity.door.status == "open":
                                    entity.door.set_status("closed", self.levels.current_map)
                                    self.message_log.send("You close the door.")
                                    self.time_counter.take_turn(1)
                                    self.game_state = GameStates.ENEMY_TURN
                                else:
                                    self.message_log.send("The door is locked.")
                                    self.time_counter.take_turn(1)
                                    self.game_state = GameStates.ENEMY_TURN
                    if "items" in self.levels.current_map.entities:
                        for entity in self.levels.current_map.entities["items"]:
                            if ((entity.x, entity.y) == (self.player.x - 1, self.player.y) or
                                    (entity.x, entity.y) == (self.player.x - 1, self.player.y - 1) or
                                    (entity.x, entity.y) == (self.player.x, self.player.y - 1) or
                                    (entity.x, entity.y) == (self.player.x + 1, self.player.y - 1) or
                                    (entity.x, entity.y) == (self.player.x + 1, self.player.y) or
                                    (entity.x, entity.y) == (self.player.x + 1, self.player.y + 1) or
                                    (entity.x, entity.y) == (self.player.x, self.player.y + 1) or
                                    (entity.x, entity.y) == (self.player.x, self.player.y) or
                                    (entity.x, entity.y) == (self.player.x - 1, self.player.y + 1)):

                                interact_msg = entity.item.interaction(self.levels.current_map)
                                if interact_msg:
                                    self.message_log.send(interact_msg)

                elif pickup:
                    if "items" in self.levels.current_map.entities:
                        for entity in self.levels.current_map.entities["items"]:
                            if entity.x == self.player.x and entity.y == self.player.y and entity.item.pickable:
                                pickup_msg = self.player.inventory.add_item(entity)
                                self.message_log.send(pickup_msg)
                                for item in self.message_log.stack:
                                    if entity.name == item.split(" ", 1)[1]:
                                        self.message_log.stack.remove(item)
                                self.levels.current_map.tiles[entity.x][entity.y].entities_on_tile.remove(entity)
                                self.levels.current_map.entities["items"].remove(entity)
                                self.time_counter.take_turn(1)
                                self.game_state = GameStates.ENEMY_TURN
                                break
                            # else:
                            #     message_log.send("There is nothing here to pick up.")
                    else:
                        self.message_log.send("There is nothing here to pick up.")

                elif stairs:
                    if "stairs" in self.levels.current_map.entities:
                        for entity in self.levels.current_map.entities["stairs"]:
                            if self.player.x == entity.x and self.player.y == entity.y:
                                self.levels.current_map.tiles[self.player.x][self.player.y].entities_on_tile.remove(self.player)
                                self.levels.change(entity.stairs.destination[0])

                        self.message_log.old_stack = self.message_log.stack

                        if self.levels.current_map.name == "cavern" and self.levels.current_map.dungeon_level == 1:
                            self.message_log.clear()
                            self.message_log.send(
                                "A sense of impending doom fills you as you delve into the cavern.")
                            self.message_log.send("RIBBIT!")

                        elif self.levels.current_map.name == "dream":
                            self.message_log.clear()
                            self.message_log.send(
                                "I'm dreaming... I feel my spirit power draining.")
                            self.message_log.send("I'm hungry..")
                        self.render_functions.draw_messages()
                        self.fov_recompute = True

                elif key == blt.TK_X:
                    self.game_state = GameStates.TARGETING
                    cursor_component = Cursor()
                    cursor = Entity(self.player.x, self.player.y, 4, 0xE800 + 1746, "light yellow", "cursor",
                                    cursor=cursor_component, stand_on_messages=False)
                    self.cursor = cursor
                    self.levels.current_map.tiles[self.cursor.x][self.cursor.y].entities_on_tile.append(self.cursor)
                    self.levels.current_map.entities["cursor"] = [self.cursor]

                if key == blt.TK_F1:
                    self.menus.avatar_info.show()
                    self.ui.draw()
                    self.ui.side_panel.draw_content()
                    self.fov_recompute = True

                if key == blt.TK_M:
                    show_msg_history(
                        self.message_log.history, "Message history", self.ui.viewport.offset_w, self.ui.viewport.offset_h)
                    self.ui.draw()
                    self.ui.side_panel.draw_content()
                    self.fov_recompute = True

                if key == blt.TK_I:
                    show_items = []
                    for item in self.player.inventory.items:
                        show_items.append(get_article(item.name) + " " + item.name)
                    show_msg_history(
                        show_items, "Inventory")
                    self.ui.draw()
                    self.ui.side_panel.draw_content()
                    self.fov_recompute = True

                if key == blt.TK_TAB:
                    test_dynamic_sprites(self.levels.current_map, self.ui)
                    self.ui.draw()
                    self.fov_recompute = True

            elif self.game_state == GameStates.TARGETING:

                if move:
                    dx, dy = move
                    destination_x = self.cursor.x + dx
                    destination_y = self.cursor.y + dy
                    x, y = self.game_camera.get_coordinates(destination_x, destination_y)

                    if 0 < x < self.game_camera.width - 1 and 0 < y < self.game_camera.height - 1:
                        prev_pos_x, prev_pos_y = self.cursor.x, self.cursor.y
                        self.cursor.move(dx, dy)
                        self.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(self.cursor)
                        self.levels.current_map.tiles[self.cursor.x][self.cursor.y].entities_on_tile.append(self.cursor)
                        self.fov_recompute = True

                        self.message_log.old_stack = self.message_log.stack
                        self.message_log.stack = []
                        if self.levels.current_map.tiles[self.cursor.x][self.cursor.y].name is not None:
                            self.message_log.stack.append(self.levels.current_map.tiles[self.cursor.x][self.cursor.y].name.capitalize())

                elif key == blt.TK_ESCAPE or key == blt.TK_X:
                    game_state = GameStates.PLAYER_TURN
                    self.message_log.old_stack = self.message_log.stack
                    self.message_log.stack = []
                    self.levels.current_map.tiles[self.cursor.x][self.cursor.y].entities_on_tile.remove(self.cursor)
                    del self.levels.current_map.entities["cursor"]
                    self.cursor = None

                if self.player.fighter.paralyzed:
                    self.message_log.send("You are paralyzed!")
                    self.time_counter.take_turn(1)
                    self.game_state = GameStates.ENEMY_TURN

            if self.game_state == GameStates.ENEMY_TURN:
                # Begin enemy turn
                self.fov_recompute = True
                self.render_functions.draw_messages()

                for entity in self.levels.current_map.entities["monsters"]:

                    if entity.fighter:
                        entity.status_effects.process_effects()

                    if self.player.fighter.dead:
                        kill_msg, game_state = kill_player(self.player)
                        self.message_log.send(kill_msg)
                        self.render_functions.draw_stats()
                        break

                    if entity.fighter and entity.fighter.dead:
                        level_up_msg = self.player.player.handle_player_exp(entity.fighter)
                        self.message_log.send(kill_monster(entity))
                        self.message_log.send("I feel my power returning!")
                        if level_up_msg:
                            self.message_log.send(level_up_msg)

                    elif entity.fighter and entity.fighter.paralyzed:
                        self.message_log.send("The monster is paralyzed!")
                        self.game_state = GameStates.PLAYER_TURN

                    elif entity.ai:
                        prev_pos_x, prev_pos_y = entity.x, entity.y
                        combat_msg = entity.ai.take_turn(
                            self.player, self.levels.current_map, self.levels.current_map.entities, self.time_counter)
                        self.levels.current_map.tiles[prev_pos_x][prev_pos_y].entities_on_tile.remove(entity)
                        self.levels.current_map.tiles[entity.x][entity.y].entities_on_tile.append(entity)
                        if entity.occupied_tiles is not None:
                            self.levels.current_map.tiles[prev_pos_x][prev_pos_y + 1].entities_on_tile.remove(entity)
                            self.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y + 1].entities_on_tile.remove(entity)
                            self.levels.current_map.tiles[prev_pos_x + 1][prev_pos_y].entities_on_tile.remove(entity)

                            self.levels.current_map.tiles[entity.x][entity.y + 1].entities_on_tile.append(entity)
                            self.levels.current_map.tiles[entity.x + 1][entity.y + 1].entities_on_tile.append(entity)
                            self.levels.current_map.tiles[entity.x + 1][entity.y].entities_on_tile.append(entity)

                        self.fov_recompute = True
                        if combat_msg:
                            self.message_log.send(combat_msg)
                            self.render_functions.draw_stats()
                        if self.player.fighter.dead:
                            kill_msg, game_state = kill_player(self.player)
                            self.message_log.send(kill_msg)
                            self.render_functions.draw_stats()
                            break
                        # Functions on monster death
                        if entity.fighter and entity.fighter.dead:
                            level_up_msg = self.player.player.handle_player_exp(entity.fighter)
                            self.message_log.send(kill_monster(entity))
                            self.message_log.send("I feel my power returning!")
                            if level_up_msg:
                                self.message_log.send(level_up_msg)

                if not self.game_state == GameStates.PLAYER_DEAD:
                    self.game_state = GameStates.PLAYER_TURN

        blt.close()

    class TimeCounter:
        def __init__(self, turn=0):
            self.turn = turn
            self.last_turn = 0

        def take_turn(self, action_cost):
            self.last_turn = self.turn
            self.turn += action_cost

        def get_turn(self):
            return self.turn

        def get_last_turn(self):
            return self.last_turn


if __name__ == '__main__':
    engine = Engine()
    engine.initialize()

