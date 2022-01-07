from data import json_data
from map_objects.tilemap import tilemap


class ChooseAnimal:
    def __init__(self, name="choose_animal", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]Choose your spirit animal..."
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.sub_menu = sub_menu
        self.margin = 6
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        self.items_icons = []
        self.sub_items = {}
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

    def show(self):
        output = self.owner.show(self)
        if not output and self.sub_menu:
            self.event = "show_prev_menu"
        else:
            self.event = None
            self.owner.handle_output(output)
