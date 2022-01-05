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
    def __init__(self, first_init=False, ui_elements=None, menu_type=None, data=None, sub_menu=False):
        self.first_init = first_init
        self.ui_elements = ui_elements
        self.menu_type = menu_type
        self.data = data
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

        elif self.menu_type == "choose_level":
            self.heading = "[color=white]Choose your destination..."
            self.margin = 6
            for item in self.data:
                name = item["title"]
                self.items.append(name)
                self.items_icons.append(0xE000 + 399)
                self.sub_items[name] = ["Rescue: Blacksmith"]

        elif self.menu_type == "avatar_info":
            self.heading = "[color=white]The following spirits have awakened within you.."
            animals = self.data.player.char
            exclude = {"player"}
            avatars = {x: animals[x] for x in animals if x not in exclude}
            for (k, v) in avatars.items():
                self.items.append(k)
                self.items_icons.append(v)
                exp = " EXP: " + str(self.data.player.char_exp[k])
                self.sub_items[k] = [exp]

    def refresh(self):
        self.ui_elements.init_ui()
        self.center_x = settings.viewport_center_x - int(len(self.heading) / 2)
        self.center_y = settings.viewport_center_y - 5
        draw_ui(self.ui_elements)

    def show(self):
        self.sel_index = 0
        output = False

        if not self.first_init and self.menu_type == "main":
            if "Graphics: " + settings.gfx in self.items:
                self.items.remove("Graphics: " + settings.gfx)
            if "Tilesize: " + settings.tile_width + "x" + settings.tile_height in self.items:
                self.items.remove("Tilesize: " + settings.tile_width + "x" + settings.tile_height)
            if "Resume game" not in self.items:
                self.items.insert(0, "Resume game")

        self.refresh()

        while not output:
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

                    # Draw icon tile
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
                if self.menu_type == "main" and self.first_init:
                    output = False
                    continue
                else:
                    break
            elif output:
                self.first_init = False
                return output
        return

    def handle_input(self, key, sel):
        output = False
        if key == blt.TK_CLOSE:
            exit()
        elif key == blt.TK_ESCAPE:
            return "break"
        elif key == blt.TK_UP:
            if self.sel_index > 0:
                self.sel_index -= 1
        elif key == blt.TK_DOWN:
            if self.sel_index < len(self.items) - 1:
                self.sel_index += 1
        elif key == blt.TK_ENTER:
            if sel == "Resume game":
                return "break"
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
                init_tiles()
                self.refresh()

            elif sel == "Tilesize: " + settings.tile_width + "x" + settings.tile_height:
                if int(settings.tile_height) == 48:
                    settings.tile_height = str(24)
                    settings.tile_width = str(16)
                else:
                    settings.tile_height = str(48)
                    settings.tile_width = str(32)
                init_tiles()
                self.refresh()
            elif sel == "New game":
                new_game_menu = Menu(ui_elements=self.ui_elements, menu_type="choose_animal", sub_menu=True)
                output = new_game_menu.show()
                del new_game_menu
            else:
                try:
                    output = self.data[self.sel_index]
                except TypeError:
                    output = sel

        return output
