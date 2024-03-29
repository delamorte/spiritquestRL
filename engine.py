import os
import pickle
import threading
from ctypes import addressof, c_uint32
from math import floor

import numpy as np
from bearlibterminal import terminal as blt

import options
from actions import Actions
from camera import Camera
from components.entity import Entity
from components.menus.main_menu import MainMenu
from components.summoner import Summoner
from data import json_data
from game_states import GameStates
from input_handlers import handle_keys
from map_gen.levels import Levels
from render_functions import RenderFunctions
from ui.elements import UIElements
from ui.menus import Menus, MenuData
from ui.message_log import MessageLog


class Engine:
    def __init__(self):
        self.debug = None
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
        self.tilemap = None
        self.data = None
        self.animations_buffer = []

    def initialize(self, debug=False):
        self.debug = debug
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

        blt.open()

        blt.set(window)
        blt.set("font: default")
        blt.set("input: filter=[keyboard]")
        #blt.composition(True)
        # Needed to avoid insta-close and flush the input queue
        blt.refresh()
        blt.read()

        if debug:
            global_options = options.Options(tile_height="24", tile_width="16", ui_size="32", debug=True)
        else:
            global_options = options.Options()
        options.data = global_options

        #self.parse_vaults_from_txt()
        x = threading.Thread(target=self.parse_vaults_from_txt, daemon=True)
        options.data.vault_thread = x
        x.start()

        # Load tiles
        self.init_tiles()
        self.init_colors()

        # Init levels for debug map view
        if debug:
            levels = Levels()
            self.levels = levels
            self.levels.owner = self

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

    def init_gfx(self, f):
        with open(f, 'rb') as gfx:
            tileset = pickle.load(gfx)

        arr = (c_uint32 * len(tileset))(*tileset)
        return arr

    def init_tiles(self,):
        tilesize = options.data.tile_width + 'x' + options.data.tile_height

        gfx1 = self.init_gfx('./gfx/gfx1')
        gfx2 = self.init_gfx('./gfx/gfx2')
        gfx3 = self.init_gfx('./gfx/gfx3')
        gfx4 = self.init_gfx('./gfx/gfx4')
        gfx5 = self.init_gfx('./gfx/gfx5')
        gfx6 = self.init_gfx('./gfx/gfx6')

        blt.set("U+E000: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx1), 304, 1184) +
                tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

        blt.set("U+E400: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx2), 320, 1080) +
                tilesize + ", resize-filter=nearest, spacing=4x4, align=top-left")

        blt.set("U+E800: %d, \
             size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx3), 288, 168) +
                tilesize + ", resize-filter=nearest, spacing=4x4 align=top-left")

        blt.set("U+F000: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx4), 176, 240) +
                "32x48" + ", resize-filter=nearest, spacing=4x4, align=top-left")

        blt.set("U+F100: %d, \
            size=32x32, raw-size=%dx%d, resize=" % (addressof(gfx5), 192, 448) +
                "32x32" + ", resize-filter=nearest, spacing=4x4, align=top-left")

        # Big tiles
        blt.set("U+F300: %d, \
            size=16x24, raw-size=%dx%d, resize=" % (addressof(gfx6), 144, 48) +
                "64x96" + ", resize-filter=nearest, spacing=4x4, align=top-left")

        options.data.tile_offset_x = int(
            int(options.data.tile_width) / blt.state(blt.TK_CELL_WIDTH))
        options.data.tile_offset_y = int(
            int(options.data.tile_height) / blt.state(blt.TK_CELL_HEIGHT))

        blt.clear()

    def init_colors(self):
        blt.set("palette.brown = #402316")
        blt.set("palette.sienna = #A0522D")
        blt.set("palette.tan = #D2B48C")
        blt.set("palette.wood = #DEB887")

    def init_new_game(self, params):
        choice = params
        self.player = None
        self.levels = None
        self.time_counter = None
        # Create player
        f_data = self.data.fighters["player"]
        summoner_component = Summoner()
        player = Entity(
            1, 1, "default", "player", layer=2,  tile=f_data,
            blocks=True, category="player", indicator_color="gray", stand_on_messages=False,
            visible=True, inventory=True, summoner=summoner_component)

        player.player.set_avatar(choice)
        player.abilities.initialize_abilities(choice)
        player.player.set_char(choice, self.data.fighters[choice])
        player.player.char_exp[choice] = player.player.avatar_exp_lvl_intervals[0]
        player.fighter.mv_spd = player.player.avatar[choice].mv_spd

        player.player.avatar[choice].max_hp += 20
        player.player.avatar[choice].hp += 20
        player.player.avatar[choice].atk += 1
        player.player.insights = 200
        
        self.player = player

        character_menu = MenuData(name="avatar_info", params=self.player)
        self.menus.create_or_show_menu(character_menu)

        level_up_menu = MenuData(name="level_up", params=self.player)
        self.menus.create_or_show_menu(level_up_menu)

        skills_menu = MenuData(name="upgrade_skills", params=self.player)
        self.menus.create_or_show_menu(skills_menu)

        message_log = MessageLog(5)
        self.message_log = message_log
        self.message_log.owner = self

        # Initialize game camera
        game_camera = Camera(1, 1, self.ui.viewport.w, self.ui.viewport.h)
        self.game_camera = game_camera
        self.game_camera.owner = self

        levels = Levels()
        self.levels = levels
        self.levels.owner = self

        blt.clear_area(2, self.ui.viewport.offset_h +
                       self.ui.offset_y + 1, self.ui.viewport.x, 1)

        if options.data.gfx == "ascii":
            player.color = "lightest green"

        self.levels.change("hub")
        self.fov_recompute = True
        self.game_state = GameStates.PLAYER_TURN
        self.time_counter = self.TimeCounter(owner=self)

    def game_loop(self):

        game_quit = False

        while not game_quit:
            if (blt.state(floor(blt.TK_WIDTH)) != self.ui.screen_w or
                    blt.state(floor(blt.TK_HEIGHT)) != self.ui.screen_h):

                self.ui = UIElements()
                self.ui.owner = self
                self.ui.draw()
                self.render_functions.draw_side_panel_content()
                blt.refresh()
                self.fov_recompute = True

            if self.fov_recompute:
                self.levels.current_map.recompute_fov(self.player)
                self.render_functions.draw_all()

            self.render_functions.draw_messages()
            self.render_functions.draw_turn_count()

            self.fov_recompute = False
            blt.refresh()

            if self.animations_buffer and options.data.gfx == "oryx":
                key = self.render_functions.draw_animations()

            else:
                key = blt.read()

            action = handle_keys(key)

            move = action.get('move')
            debug_map = action.get('debug_map')
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
            level_up = action.get('level_up')
            upgrade_skills = action.get('upgrade_skills')
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

            if self.game_state == GameStates.PLAYER_TURN:
                # Begin player turn
                # Non-turn taking UI functions

                if self.actions.menu_actions(main_menu=main_menu,
                                             avatar_info=avatar_info,
                                             inventory=inventory,
                                             msg_history=msg_history,
                                             level_up=level_up,
                                             upgrade_skills=upgrade_skills,
                                             debug_map=debug_map):
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
                self.actions.ally_actions()

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

    @staticmethod
    def parse_vaults_from_txt():
        '''
        Parse vaults from Zorbus format into rooms
        Vault prefabs kindly provided by joonas@zorbus.net under the CC0 Creative Commons License:
        http://dungeon.zorbus.net/
        '''

        vaults = []
        vaults_path = options.data.vaults_path

        for filename in os.listdir(vaults_path):
            if filename.endswith(".txt"):
                vault_file = vaults_path + filename
                with open(vault_file) as file:
                    file_lines = file.readlines()

                    numpy_vault = np.array([list(i) for i in file_lines], dtype=str)[:, :-1]
                    numpy_vault = np.where(numpy_vault == ' ', "1", numpy_vault)
                    numpy_vault = np.where(numpy_vault == '#', "1", numpy_vault)
                    numpy_vault = np.where(numpy_vault == '.', "0", numpy_vault)
                    numpy_vault = numpy_vault.astype(int)

                    floors = np.where(numpy_vault == 0)
                    trimmed_room = numpy_vault[floors[0].min():floors[0].max() + 1,
                                   floors[1].min():floors[1].max() + 1]

                    room = np.pad(trimmed_room, 1, constant_values=1)
                    vaults.append(room)

        options.data.vaults_data = vaults

if __name__ == '__main__':
    engine = Engine()
    engine.initialize(debug=False)
    blt.close()

