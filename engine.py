from bearlibterminal import terminal as blt

from actions import Actions
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
        self.actions = None
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

        self.actions = Actions()
        self.actions.owner = self

        self.render_functions = RenderFunctions(self.ui.offset_x, self.ui.offset_y)
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
        self.player = None
        self.levels = None
        self.time_counter = None
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
        game_camera = Camera(1, 1, self.ui.viewport.w, self.ui.viewport.h)
        self.game_camera = game_camera
        self.game_camera.owner = self

        levels = Levels()
        self.levels = levels
        self.levels.owner = self

        self.time_counter = self.TimeCounter()

        blt.clear_area(2, self.ui.viewport.offset_h +
                       self.ui.offset_y + 1, self.ui.viewport.x, 1)

        # if settings.gfx == "ascii":
        #     player.char = tilemap()["player"]
        #     player.color = "lightest green"

        self.levels.change("hub")
        self.fov_recompute = True
        self.game_state = GameStates.PLAYER_TURN

    def game_loop(self):

        game_quit = False

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
            wait = action.get('wait')
            pickup = action.get('pickup')
            interact = action.get("interact")
            stairs = action.get('stairs')
            examine = action.get('examine')
            minimap = action.get('map')
            fullscreen = action.get('fullscreen')
            close = action.get('close')
            main_menu = action.get('main_menu')
            avatar_info = action.get('avatar_info')
            inventory = action.get('inventory')
            msg_history = action.get('msg_history')

            if self.actions.window_actions(fullscreen=fullscreen, close=close):
                continue

            if self.game_state == GameStates.PLAYER_DEAD:
                while self.game_state == GameStates.PLAYER_DEAD:
                    key = blt.read()
                    if self.actions.dead_actions(key):
                        continue

            if not self.player.fighter.dead:
                self.player.status_effects.process_effects()

            if self.player.fighter.paralyzed:
                self.message_log.send("You are paralyzed!")
                self.time_counter.take_turn(1)
                self.game_state = GameStates.ENEMY_TURN

            if self.game_state == GameStates.PLAYER_TURN:
                # Begin player turn
                # Non-turn taking UI functions

                if self.actions.menu_actions(main_menu=main_menu,
                                             avatar_info=avatar_info,
                                             inventory=inventory,
                                             msg_history=msg_history):
                    continue

                # Turn taking functions

                self.actions.turn_taking_actions(wait=wait,
                                                 move=move,
                                                 interact=interact,
                                                 pickup=pickup,
                                                 stairs=stairs,
                                                 examine=examine)

            elif self.game_state == GameStates.TARGETING:

                if self.actions.targeting_actions(move=move,
                                                  examine=examine,
                                                  main_menu=main_menu):
                    continue

            if self.game_state == GameStates.ENEMY_TURN:
                # Begin enemy turn
                self.actions.enemy_actions()

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
    blt.close()

