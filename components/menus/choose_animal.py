from bearlibterminal import terminal as blt

import options
from data import json_data
from map_objects import tilemap


class ChooseAnimal:
    def __init__(self, name="choose_animal", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]Choose your spirit animal..."
        self.sub_heading = None
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.sub_menu = sub_menu
        self.margin_x = 10
        self.margin_y = 6
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        initial_animals = {x: self.data.fighters[x] for x in options.data.initial_animals}
        for k in initial_animals:
            animal = initial_animals[k]
            stats = "hp: {0}, ac: {1}, ev: {2}, power: {3}".format(animal["hp"], animal["ac"], animal["ev"],
                                                                   animal["atk"])
            skills = "skills: {0}".format(", ".join(animal["player_abilities"]))
            self.items.append(k)
            if options.data.gfx == "ascii":
                self.items_icons.append(animal["ascii"])
            else:
                self.items_icons.append(animal["tile"])
            self.sub_items[k] = [stats, skills]

    def show(self):
        output = self.owner.show(self)
        if not output and self.sub_menu:
            self.event = "show_prev_menu"
        else:
            self.event = None
            self.owner.handle_output(output)
