from math import floor

from bearlibterminal import terminal as blt

from components.menus.avatar_info import AvatarInfo
from components.menus.choose_animal import ChooseAnimal
from components.menus.choose_level import ChooseLevel
from game_states import GameStates
from color_functions import get_monster_color
from map_objects.tilemap import init_tiles
from ui.elements import UIElements


class Menus:
    def __init__(self, main_menu=None, choose_animal=None, choose_level=None, avatar_info=None):
        self.owner = None
        self.main_menu = main_menu
        self.choose_animal = choose_animal
        self.choose_level = choose_level
        self.avatar_info = avatar_info
        self.current_menu = None
        self.text_wrap = 50
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

    def refresh(self, heading):
        self.center_x = self.owner.ui.viewport.offset_center_x - int(len(heading) / 2)
        self.center_y = self.owner.ui.viewport.offset_center_y - 5
        self.viewport_w = self.owner.ui.viewport.offset_w
        self.viewport_h = self.owner.ui.viewport.offset_h
        #self.owner.ui.draw()

    def show(self, menu):
        self.current_menu = menu
        self.owner.game_state = GameStates.MENU
        self.sel_index = 0
        output = None
        self.refresh(menu.heading)

        while not output:
            if (blt.state(floor(blt.TK_WIDTH)) != self.owner.ui.screen_w or
                    blt.state(floor(blt.TK_HEIGHT)) != self.owner.ui.screen_h):

                init_tiles(self.owner.options)
                self.owner.ui = UIElements()
                self.owner.ui.owner = self.owner
                self.refresh(menu.heading)
                self.owner.ui.draw()
                blt.refresh()
                self.owner.fov_recompute = True

            blt.layer(0)
            self.owner.render_functions.clear_camera(5)
            blt.puts(self.center_x, self.center_y - 5,
                     menu.heading, 0, 0, blt.TK_ALIGN_LEFT)

            for i, sel in enumerate(menu.items):
                selected = i == self.sel_index
                blt.color("orange" if selected else "light_gray")
                blt.puts(self.center_x, self.center_y + i * menu.margin, "%s%s" %
                         ("[U+203A]" if selected else " ", sel), 0, 0, blt.TK_ALIGN_LEFT)

                if sel in menu.sub_items:
                    for j, sub_sel in enumerate(menu.sub_items[sel]):
                        blt.puts(self.center_x, self.center_y + i * menu.margin + j + 2,
                                 sub_sel, self.text_wrap, 0, blt.TK_ALIGN_LEFT)

                if menu.items_icons:
                    # Draw icon tile
                    blt.layer(1)
                    blt.color(get_monster_color(sel))
                    # if settings.gfx == "ascii":
                    #     blt.puts(self.center_x - 6 + 1,
                    #              self.center_y - 2 + i * 5, items_icons[i], 0, 0)

                    blt.puts(self.center_x - 6 + 1, self.center_y +
                             i * menu.margin, "[U+" + hex(menu.items_icons[i]) + "]", 0, 0)

            blt.refresh()

            sel = menu.items[self.sel_index]
            key = blt.read()

            output = self.handle_input(key, sel, menu.items)
            if output == "break":
                if menu.title_screen:
                    output = None
                    continue
                else:
                    self.owner.game_state = GameStates.PLAYER_TURN
                    break
            elif output:
                return output

    def handle_input(self, key, sel, items):
        output = None
        if key == blt.TK_CLOSE:
            exit()
        elif key == blt.TK_ESCAPE:
            return "break"
        elif key == blt.TK_UP:
            if self.sel_index > 0:
                self.sel_index -= 1
        elif key == blt.TK_DOWN:
            if self.sel_index < len(items) - 1:
                self.sel_index += 1
        elif key == blt.TK_ENTER:
            if sel == "Resume game":
                return "break"
            elif sel == "Exit":
                exit()
            elif sel == "New game":
                output = MenuData(name="choose_animal", sub_menu=True, prev_menu=self.current_menu)
            elif self.current_menu.name == "choose_animal":
                output = MenuData(params=sel, event="new_game")
            else:
                output = MenuData(params=sel)

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

        self.owner.game_state = GameStates.PLAYER_TURN
        #self.owner.ui.draw()


class MenuData:
    def __init__(self, name=None, sub_menu=False, prev_menu=None, params=None, event=None):
        self.name = name
        self.sub_menu = sub_menu
        self.prev_menu = prev_menu
        self.params = params
        self.event = event
