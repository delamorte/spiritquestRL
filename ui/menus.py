from math import floor

from bearlibterminal import terminal as blt

import options
from components.menus.avatar_info import AvatarInfo
from components.menus.choose_animal import ChooseAnimal
from components.menus.choose_level import ChooseLevel
from components.menus.level_up import LevelUp
from components.menus.upgrade_skills import UpgradeSkills
from game_states import GameStates
from color_functions import get_monster_color
from map_objects import tilemap
from ui.elements import UIElements


class Menus:
    def __init__(self, main_menu=None, choose_animal=None, choose_level=None, avatar_info=None,
                 level_up=None, upgrade_skills=None):
        self.owner = None
        self.main_menu = main_menu
        self.choose_animal = choose_animal
        self.choose_level = choose_level
        self.avatar_info = avatar_info
        self.level_up = level_up
        self.upgrade_skills = upgrade_skills
        self.current_menu = None
        self.text_wrap = 60
        self.sel_index = 0
        self.center_x = 0
        self.center_y = 0
        self.viewport_w = 0
        self.viewport_h = 0

        if self.main_menu:
            self.main_menu.owner = self
        if self.choose_animal:
            self.choose_animal.owner = self
        if self.choose_level:
            self.choose_level.owner = self
        if self.avatar_info:
            self.avatar_info.owner = self
        if self.level_up:
            self.level_up.owner = self
        if self.upgrade_skills:
            self.upgrade_skills.owner = self

    def refresh(self):
        self.center_x = self.owner.ui.viewport.offset_center_x
        self.center_y = self.owner.ui.viewport.offset_center_y - 5
        self.viewport_w = self.owner.ui.viewport.offset_w
        self.viewport_h = self.owner.ui.viewport.offset_h

    def show(self, menu):
        self.current_menu = menu
        self.owner.game_state = GameStates.MENU
        self.sel_index = 0
        output = MenuData()
        self.refresh()

        while output.menu_actions_left:
            if (blt.state(floor(blt.TK_WIDTH)) != self.owner.ui.screen_w or
                    blt.state(floor(blt.TK_HEIGHT)) != self.owner.ui.screen_h):

                self.owner.ui = UIElements()
                self.owner.ui.owner = self.owner
                self.refresh()
                self.owner.ui.draw()
                blt.refresh()
                self.owner.fov_recompute = True

            blt.layer(0)
            self.owner.render_functions.clear_camera(5)
            blt.puts(int(self.center_x / 2) + menu.margin_x, self.center_y - 5,
                     menu.heading, self.text_wrap, 0, menu.align)

            if menu.sub_heading:
                blt.puts(int(self.center_x / 2) + menu.margin_x, self.center_y - 3,
                         menu.sub_heading, self.text_wrap, 0, menu.align)

            for i, sel in enumerate(menu.items):
                selected = i == self.sel_index
                blt.color("orange" if selected else "light_gray")
                blt.puts(int(self.center_x / 2) + menu.margin_x, self.center_y + i * menu.margin_y, "%s%s" %
                         ("[U+203A]" if selected else " ", sel), self.text_wrap, 0, menu.align)

                if sel in menu.sub_items:
                    for j, sub_sel in enumerate(menu.sub_items[sel]):
                        blt.puts(int(self.center_x / 2) + menu.margin_x, self.center_y + i * menu.margin_y + j + 1,
                                 sub_sel, self.text_wrap, 0, menu.align)

                if menu.items_icons:
                    # Draw icon tile
                    blt.layer(1)
                    blt.color(get_monster_color(sel))
                    if options.data.gfx == "ascii":
                        blt.puts(int(self.center_x / 2),
                                 self.center_y + i * menu.margin_y, menu.items_icons[i], 0, 0, menu.align)
                    else:

                        blt.puts(int(self.center_x / 2), self.center_y +
                                 i * menu.margin_y - 1, "[U+" + hex(menu.items_icons[i]) + "]", 0, 0, menu.align)

            blt.refresh()

            sel = menu.items[self.sel_index]
            key = blt.read()

            output = self.handle_input(output, key, sel, menu.items)
            if output.event == "break":
                if menu.title_screen:
                    output = None
                    continue
                else:
                    self.owner.game_state = GameStates.PLAYER_TURN
                    break
            elif output.params or output.sub_menu or not output.menu_actions_left:
                return output

    def handle_input(self, output, key, sel, items):

        if key == blt.TK_CLOSE:
            exit()
        elif key == blt.TK_ESCAPE:
            output.event = "break"
            return output
        elif key == blt.TK_UP:
            if self.sel_index > 0:
                self.sel_index -= 1
        elif key == blt.TK_DOWN:
            if self.sel_index < len(items) - 1:
                self.sel_index += 1
        elif key == blt.TK_ENTER:
            if sel == "Resume game":
                output.event = "break"
                return output
            elif sel == "Exit":
                exit()
            elif sel == "New game":
                output.name = "choose_animal"
                output.sub_menu = True
                output.prev_menu = self.current_menu
            elif self.current_menu.name == "choose_animal":
                output.params = sel
                output.event = "new_game"
            elif self.current_menu.name == "level_up":
                output.params = sel
                output.event = "level_up"
            elif self.current_menu.name == "upgrade_skills":
                output.params = sel
                output.event = "upgrade_skills"
                output = self.current_menu.spend_points(output)
            else:
                output.params = sel

        return output

    def handle_output(self, data):
        if data.sub_menu:
            self.create_or_show_menu(data)
            if self.current_menu.event == "show_prev_menu":
                data.prev_menu.show()
        elif data.event == "new_game":
            self.owner.init_new_game(params=data.params)
        elif self.current_menu.event == "level_change":
            self.owner.levels.params = data.params
        self.owner.game_state = GameStates.PLAYER_TURN

    def create_or_show_menu(self, data):
        blt.layer(1)
        self.owner.render_functions.clear_camera(5)

        if data.name == "choose_animal":
            if self.choose_animal:
                self.choose_animal.refresh()
                self.choose_animal.show()
            else:
                choose_animal_menu = ChooseAnimal(sub_menu=data.sub_menu)
                self.choose_animal = choose_animal_menu
                self.choose_animal.owner = self
                self.choose_animal.show()
        elif data.name == "choose_level":
            if self.choose_level:
                self.choose_level.data = data.params
                self.choose_level.refresh()
                self.choose_level.show()
            else:
                choose_level_menu = ChooseLevel(data=data.params)
                self.choose_level = choose_level_menu
                self.choose_level.owner = self
                self.choose_level.show()
        elif data.name == "avatar_info":
            if self.avatar_info:
                self.avatar_info.data = data.params
                self.avatar_info.refresh()
                self.avatar_info.show()
            else:
                avatar_info_menu = AvatarInfo(data=data.params)
                self.avatar_info = avatar_info_menu
                self.avatar_info.owner = self
                self.avatar_info.show()
        elif data.name == "level_up":
            if self.level_up:
                self.level_up.data = data.params
                self.level_up.refresh()
            else:
                level_up_menu = LevelUp(data=data.params)
                self.level_up = level_up_menu
                self.level_up.owner = self
        elif data.name == "upgrade_skills":
            if self.upgrade_skills:
                self.upgrade_skills.data = data.params
                self.upgrade_skills.refresh()
            else:
                upgrade_skills_menu = UpgradeSkills(data=data.params)
                self.upgrade_skills = upgrade_skills_menu
                self.upgrade_skills.owner = self

        self.owner.game_state = GameStates.PLAYER_TURN


class MenuData:
    def __init__(self, name=None, sub_menu=False, prev_menu=None, params=None, event=None, menu_actions_left=True):
        self.name = name
        self.sub_menu = sub_menu
        self.prev_menu = prev_menu
        self.params = params
        self.event = event
        self.menu_actions_left = menu_actions_left
        self.messages = []
