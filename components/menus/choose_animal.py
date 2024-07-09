from bearlibterminal import terminal as blt

import options
from components.menus.menu_item import MenuItem
from data import json_data
from map_gen.tilemap import get_tile


class ChooseAnimal:
    def __init__(self, name="choose_animal", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]Choose your spirit animal..."
        self.items = []
        self.sub_menu = sub_menu
        self.margin_x = 10
        self.margin_y = 6
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        animals = {x: json_data.data.fighters[x] for x in options.data.initial_animals}
        for k in animals:
            animal = animals[k]
            stats = "\n hp: {0}, ac: {1}, ev: {2}, power: {3}".format(animal["hp"], animal["ac"], animal["ev"],
                                                                   animal["atk"])
            skills = "\n skills: {0}".format(", ".join(animal["player_abilities"]))
            tile = get_tile(k)
            icon = tile
            item_str = k + stats + skills
            menu_item = MenuItem(k, item_str, icon)
            self.items.append(menu_item)


    def show(self):
        output = self.owner.show(self)
        if not output and self.sub_menu:
            self.event = "show_prev_menu"
        else:
            self.event = None
            self.owner.handle_output(output)
