from bearlibterminal import terminal as blt

from data import json_data
from descriptions import abilities, bestiary, meditate_params
from draw import clear_camera, draw_ui
from map_objects.tilemap import init_tiles, tilemap
import settings
from random import sample
from palettes import get_monster_color
from os import path
from textwrap import wrap
import settings


class Menu:
    def __init__(self, first_init=False, ui_elements=None, menu_type=None, sub_menu=False):
        self.first_init = first_init
        self.ui_elements = ui_elements
        self.menu_type = menu_type
        self.heading = None
        self.margin = 1
        self.text_wrap = 50
        self.sel_index = 0
        self.center_x = settings.viewport_center_x
        self.center_y = settings.viewport_center_y
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.sub_menus = []
        self.sub_menu = sub_menu
        self.init_items()

    def init_items(self):
        if self.menu_type == "main":
            self.heading = "[color=white]Spirit Quest RL"
            self.items = ["New game",
                          "Graphics: " + settings.gfx,
                          "Tilesize: " + settings.tile_width + "x" + settings.tile_height,
                          "Exit"]

        elif self.menu_type == "choose_animal":
            self.heading = "[color=white]Choose your spirit animal..."
            self.margin = 6
            animals = tilemap()["monsters"]
            animals = {x: animals[x] for x in ("crow", "rat", "snake")}
            for (k, v) in animals.items():
                animal = json_data.data.fighters[k]
                stats = "hp: {0}, ac: {1}, ev: {2}, power: {3}".format(animal["hp"], animal["ac"], animal["ev"],
                                                                       animal["power"])
                skills = "skills: {0}".format(", ".join(animal["player_abilities"]))
                self.items.append(k)
                self.items_icons.append(v)
                self.sub_items[k] = [stats, skills]

    def refresh(self):
        init_tiles()
        self.ui_elements.init_ui()
        self.center_x = settings.viewport_center_x - int(len(self.heading)/2)
        self.center_y = settings.viewport_center_y
        draw_ui(self.ui_elements)

    def show(self):

        self.sel_index = 0
        output = False

        self.refresh()

        while not output:
            if not self.first_init and self.menu_type == "main":
                if "Graphics: " + settings.gfx in self.items:
                    self.items.remove("Graphics: " + settings.gfx)
                if "Tilesize: " + settings.tile_width + "x" + settings.tile_height in self.items:
                    self.items.remove("Tilesize: " + settings.tile_width + "x" + settings.tile_height)
                self.items.insert(0, "Resume game")

            blt.layer(0)
            clear_camera(5)
            blt.puts(self.center_x, self.center_y - 5,
                     self.heading, 0, 0, blt.TK_ALIGN_LEFT)

            for i, sel in enumerate(self.items):
                selected = i == self.sel_index
                blt.color("orange" if selected else "light_gray")
                blt.puts(self.center_x, self.center_y + i * self.margin, "%s%s" %
                         ("[U+203A]" if selected else " ", sel), 0, 0, blt.TK_ALIGN_LEFT)

                if sel in self.sub_items:
                    for j, sub_sel in enumerate(self.sub_items[sel]):
                        blt.puts(self.center_x, self.center_y + i * self.margin + j + 2,
                                 sub_sel, self.text_wrap, 0, blt.TK_ALIGN_LEFT)

                if self.items_icons:
                    # Draw a bg tile
                    if settings.gfx == "adambolt":
                        blt.layer(0)
                        blt.puts(self.center_x - 6 + 1, self.center_y + i *
                                 self.margin, "[U+" + hex(0xE800 + 3) + "]", 0, 0)

                    # Draw monster tile
                    blt.layer(1)
                    blt.color(get_monster_color(sel))
                    if settings.gfx == "adambolt":
                        blt.color(None)
                    if settings.gfx == "ascii":
                        blt.puts(self.center_x - 6 + 1,
                                 self.center_y - 2 + i * 5, self.items_icons[i], 0, 0)
                    else:
                        blt.puts(self.center_x - 6 + 1, self.center_y +
                                 i * self.margin, "[U+" + hex(self.items_icons[i]) + "]", 0, 0)

            blt.refresh()

            sel = self.items[self.sel_index]
            key = blt.read()

            output = self.handle_input(key, sel)
            if output == "break":
                break
            elif output:
                return output

    def choose_mission(self, levels):

        current_range = 0
        center_x = settings.viewport_center_x
        center_y = settings.viewport_center_y

        while True:
            clear_camera(5)
            blt.layer(0)
            blt.puts(center_x, center_y - 5,
                     "[color=white]Choose your destination...", 0, 0, blt.TK_ALIGN_CENTER)

            choice = None
            for i, level in enumerate(levels):
                selected = i == current_range

                # Draw select symbol, destination name and description
                blt.color("orange" if selected else "default")
                blt.puts(center_x - 24, center_y - 2 + i * 3, "%s%s" %
                         ("[U+203A]" if selected else " ", level["title"] + "\n " + "Rescue: Blacksmith"), 0, 0,
                         blt.TK_ALIGN_LEFT)

                if settings.gfx == "adambolt":
                    # Draw a bg tile
                    blt.layer(0)
                    blt.puts(center_x - 30 + 1, center_y - 2 + i *
                             5, "[U+" + hex(0xE800 + 3) + "]", 0, 0)

                # Draw map tile
                blt.layer(1)
                blt.color("dark green")
                if settings.gfx == "adambolt":
                    blt.color(None)
                if settings.gfx == "ascii":
                    blt.puts(center_x - 30 + 1, center_y - 2 + i * 3, "#", 0, 0)
                else:
                    blt.puts(center_x - 30 + 1, center_y - 2 + i *
                             3, "[U+" + hex(0xE000 + 399) + "]", 0, 0)

                if selected:
                    choice = level

            blt.refresh()
            key = blt.read()

            if key == blt.TK_ESCAPE:
                return None
            elif key == blt.TK_UP:
                if current_range > 0:
                    current_range -= 1
            elif key == blt.TK_DOWN:
                if current_range < len(levels) - 1:
                    current_range += 1
            elif key == blt.TK_ENTER:
                return choice


    def set_up_level_params(self, question_number, prev_choices):
        current_range = 0
        center_x = settings.viewport_center_x
        center_y = settings.viewport_center_y
        choice_params = dict(sample(meditate_params().items(), 3))
        choice_params = {x: choice_params[x] for x in choice_params if x not in prev_choices}

        while True:
            clear_camera(2)
            blt.layer(0)
            if question_number == 0:
                blt.puts(center_x, center_y - 5,
                         "[color=white]You sit by the campfire to meditate. The world begins to drift away... ", 0, 0,
                         blt.TK_ALIGN_CENTER)
                blt.puts(center_x, center_y - 4,
                         "[color=white]Your mind gets visions of..", 0, 0, blt.TK_ALIGN_CENTER)
            if question_number == 1:
                blt.puts(center_x, center_y - 5,
                         "[color=white]Pictures of " + list(prev_choices)[0] + " begin to form in your mind.", 0, 0,
                         blt.TK_ALIGN_CENTER)
                blt.puts(center_x, center_y - 4,
                         "[color=white]Then, a new image appears..", 0, 0, blt.TK_ALIGN_CENTER)

            if question_number == 2:
                blt.puts(center_x, center_y - 5,
                         "[color=white]You have dreamt about " + list(prev_choices)[0] + ", which shall bring about " +
                         list(prev_choices)[1] + ".", 0, 0, blt.TK_ALIGN_CENTER)
                blt.puts(center_x, center_y - 4,
                         "[color=white]The last thing that enters your mind is...", 0, 0, blt.TK_ALIGN_CENTER)

            for i, r in enumerate(choice_params):
                selected = i == current_range
                blt.color("orange" if selected else "light_gray")
                blt.puts(center_x + 2, center_y + 2 + i, "%s%s" %
                         ("[U+203A]" if selected else " ", ".." + r + "."), 0, 0, blt.TK_ALIGN_CENTER)

                if selected:
                    choice = {r: choice_params[r]}

            blt.refresh()
            key = blt.read()

            if key == blt.TK_ESCAPE:
                break
            elif key == blt.TK_UP:
                if current_range > 0:
                    current_range -= 1
            elif key == blt.TK_DOWN:
                if current_range < len(choice_params) - 1:
                    current_range += 1
            elif key == blt.TK_ENTER:
                return choice


    def character_menu(self, player):
        current_range = 0
        center_x = settings.viewport_center_x
        center_y = settings.viewport_center_y

        while True:
            clear_camera(5)
            animals = player.player.char
            exclude = {"player"}
            avatars = {x: animals[x] for x in animals if x not in exclude}
            blt.layer(0)
            blt.puts(center_x, center_y - 5,
                     "[color=white]The following spirits have awakened within you..", 0, 0, blt.TK_ALIGN_CENTER)
            for i, (r, c) in enumerate(avatars.items()):
                selected = i == current_range

                # Draw select symbol, monster name and description
                blt.color("orange" if selected else "default")
                blt.puts(center_x - 24, center_y - 2 + i * 4, "%s%s" %
                         ("[U+203A]" if selected else " ", r.capitalize() + ":" + "\n " + bestiary()[r]), 0, 0,
                         blt.TK_ALIGN_LEFT)

                # Put exp amount
                blt.puts(center_x - 24, center_y - 2 + i * 4+2, " EXP: " + str(player.player.char_exp[r]) +"\n ", 0, 0,
                         blt.TK_ALIGN_LEFT)

                if settings.gfx == "adambolt":
                    # Draw a bg tile
                    blt.layer(0)
                    blt.puts(center_x - 30 + 1, center_y - 2 + i *
                             6, "[U+" + hex(0xE800 + 3) + "]", 0, 0)

                # Draw monster tile
                blt.layer(1)
                blt.color(get_monster_color(r))
                if settings.gfx == "adambolt":
                    blt.color(None)
                if settings.gfx == "ascii":
                    blt.puts(center_x - 30 + 1, center_y - 2 + i * 4, c, 0, 0)
                else:
                    blt.puts(center_x - 30 + 1, center_y - 2 + i *
                             4, "[U+" + hex(c) + "]", 0, 0)

                if selected:
                    choice = r

            blt.refresh()
            key = blt.read()

            if key == blt.TK_ESCAPE:
                return None, None
            elif key == blt.TK_UP:
                if current_range > 0:
                    current_range -= 1
            elif key == blt.TK_DOWN:
                if current_range < len(avatars) - 1:
                    current_range += 1

    def handle_input(self, key, sel):
        output = False
        if key == blt.TK_CLOSE:
            exit()
        elif key == blt.TK_ESCAPE and self.sub_menu:
            return "break"
        elif key == blt.TK_ESCAPE:
            exit()
        elif key == blt.TK_UP:
            if self.sel_index > 0:
                self.sel_index -= 1
        elif key == blt.TK_DOWN:
            if self.sel_index < len(self.items) - 1:
                self.sel_index += 1
        elif key == blt.TK_ENTER:
            if sel == "Resume game":
                return False
            elif sel == "Exit":
                exit()
            elif sel == "Graphics: " + settings.gfx:
                if settings.gfx == "adambolt":
                    settings.gfx = "ascii"
                    settings.tile_height = str(24)
                    settings.tile_width = str(16)
                elif settings.gfx == "ascii":
                    settings.gfx = "oryx"
                    settings.tile_height = str(48)
                    settings.tile_width = str(32)
                elif settings.gfx == "oryx":
                    settings.gfx = "adambolt"
                    settings.tile_height = str(48)
                    settings.tile_width = str(32)
                self.refresh()

            elif sel == "Tilesize: " + settings.tile_width + "x" + settings.tile_height:
                if int(settings.tile_height) == 48:
                    settings.tile_height = str(24)
                    settings.tile_width = str(16)
                else:
                    settings.tile_height = str(48)
                    settings.tile_width = str(32)
                self.refresh()
            elif sel == "New game":
                new_game_menu = Menu(ui_elements=self.ui_elements, menu_type="choose_animal", sub_menu=True)
                self.sub_menus.append(new_game_menu)
                output = new_game_menu.show()
            else:
                output = sel

        return output
