from math import floor

from bearlibterminal import terminal as blt

from actions import Actions
from camera import Camera
from color_functions import argb_from_color
from components.abilities import Abilities
from components.entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory
from components.light_source import LightSource
from components.menus.main_menu import MainMenu
from components.player import Player
from components.status_effects import StatusEffects
from components.summoner import Summoner
from data import json_data
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.levels import Levels
from map_objects.tilemap import init_tiles, tilemap
from options import Options
from render_functions import RenderFunctions
from ui.elements import UIElements
from ui.menus import Menus, MenuData
from ui.message_log import MessageLog


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
        self.options = None
        self.data = None
        self.animations_buffer = []

    def initialize(self):
        # Initialize game data from external files
        game_data = json_data.JsonData()
        json_data.data = game_data
        self.data = game_data

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

        self.options = Options()

        # Load tiles
        init_tiles(self.options)

        # Init UI
        self.ui = UIElements()
        self.ui.owner = self

        self.actions = Actions()
        self.actions.owner = self

        self.render_functions = RenderFunctions(self.ui.offset_x, self.ui.offset_y)
        self.render_functions.owner = self

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
        f_data = self.data.fighters["player"]
        fighter_component = Fighter(hp=f_data["hp"], ac=f_data["ac"], ev=f_data["ev"],
                                    power=f_data["power"], mv_spd=f_data["mv_spd"],
                                    atk_spd=f_data["atk_spd"], size=f_data["size"], fov=f_data["fov"])

        light_component = LightSource(radius=fighter_component.fov)
        player_component = Player(50)
        abilities_component = Abilities("player")
        status_effects_component = StatusEffects("player")
        summoner_component = Summoner()
        player = Entity(
            1, 1, 3, player_component.char["player"], "default", "player", blocks=True, player=player_component,
            fighter=fighter_component, inventory=inventory_component, light_source=light_component,
            summoner=summoner_component, indicator_color="gray",
            abilities=abilities_component, status_effects=status_effects_component, stand_on_messages=False)
        player.player.avatar["player"] = fighter_component
        avatar_f_data = self.data.fighters[choice]
        a_fighter_component = Fighter(hp=avatar_f_data["hp"], ac=avatar_f_data["ac"], ev=avatar_f_data["ev"],
                                      power=avatar_f_data["power"], mv_spd=avatar_f_data["mv_spd"],
                                      atk_spd=avatar_f_data["atk_spd"], size=avatar_f_data["size"],
                                      fov=avatar_f_data["fov"])
        player.player.avatar[choice] = a_fighter_component
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
        game_camera = Camera(1, 1, self.ui.viewport.w, self.ui.viewport.h, self.options)
        self.game_camera = game_camera
        self.game_camera.owner = self

        levels = Levels(tileset=self.options.gfx)
        self.levels = levels
        self.levels.owner = self

        blt.clear_area(2, self.ui.viewport.offset_h +
                       self.ui.offset_y + 1, self.ui.viewport.x, 1)

        # if settings.gfx == "ascii":
        #     player.char = tilemap()["player"]
        #     player.color = "lightest green"

        self.levels.change("hub")
        self.fov_recompute = True
        self.game_state = GameStates.PLAYER_TURN
        self.time_counter = self.TimeCounter(owner=self)



    def game_loop(self):

        game_quit = False

        while not game_quit:

            if (blt.state(floor(blt.TK_WIDTH)) != self.ui.screen_w or
                    blt.state(floor(blt.TK_HEIGHT)) != self.ui.screen_h):

                init_tiles(self.options)
                self.ui = UIElements()
                self.ui.owner = self
                self.ui.draw()
                blt.refresh()
                self.fov_recompute = True

            if self.fov_recompute:
                self.player.light_source.recompute_fov(self.player.x, self.player.y)
                self.player.player.init_light()
                self.render_functions.draw_all()

            self.render_functions.draw_messages()
            self.render_functions.draw_turn_count()

            for icon, alpha in self.animations_buffer:
                blt.layer(4)
                x, y = self.game_camera.get_coordinates(self.player.x, self.player.y)
                c = blt.color_from_name("amber")
                argb = argb_from_color(c)
                a = alpha
                r = argb[1]
                g = argb[2]
                b = argb[3]

                blt.color(blt.color_from_argb(a, r, g, b))
                blt.put_ext(x * self.options.tile_offset_x-2, y *
                        self.options.tile_offset_y-2, -5, 5, icon)
                blt.delay(100)
                blt.refresh()
                blt.clear_area(x * self.options.tile_offset_x, y *
                        self.options.tile_offset_y, 1, 1)

            self.animations_buffer = []

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
            # minimap = action.get('map')
            fullscreen = action.get('fullscreen')
            close = action.get('close')
            main_menu = action.get('main_menu')
            avatar_info = action.get('avatar_info')
            inventory = action.get('inventory')
            msg_history = action.get('msg_history')
            switch_ability = action.get('switch_ability')
            use_ability = action.get('use_ability')

            if self.actions.window_actions(fullscreen=fullscreen, close=close):
                continue

            if self.game_state == GameStates.PLAYER_DEAD:
                while self.game_state == GameStates.PLAYER_DEAD:
                    if self.actions.dead_actions(key):
                        break
                    key = blt.read()
                continue

            self.actions.ally_actions()

            if self.game_state == GameStates.PLAYER_TURN:
                # Begin player turn
                # Non-turn taking UI functions

                if self.actions.menu_actions(main_menu=main_menu,
                                             avatar_info=avatar_info,
                                             inventory=inventory,
                                             msg_history=msg_history):
                    continue

                elif self.actions.ability_actions(switch=switch_ability, key=key):
                    continue

                # Turn taking functions

                self.actions.turn_taking_actions(wait=wait,
                                                 move=move,
                                                 interact=interact,
                                                 pickup=pickup,
                                                 stairs=stairs,
                                                 examine=examine,
                                                 use_ability=use_ability,
                                                 key=key)

            elif self.game_state == GameStates.TARGETING:

                if self.actions.targeting_actions(move=move,
                                                  examine=examine,
                                                  main_menu=main_menu,
                                                  use_ability=use_ability,
                                                  interact=interact):
                    continue

            if self.game_state == GameStates.ENEMY_TURN:
                # Begin enemy turn
                self.actions.enemy_actions()

    class TimeCounter:
        def __init__(self, turn=0, owner=None):
            self.owner = owner
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

