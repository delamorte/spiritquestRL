from random import choice

from bearlibterminal import terminal as blt

import options
from map_gen.tilemap import get_tile


class ChooseLevel:
    def __init__(self, name="choose_level", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]Choose your destination..."
        self.sub_heading = None
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.sub_menu = sub_menu
        self.margin_x = 6
        self.margin_y = 6
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        for item in self.data:
            name = item.title
            self.items.append(name)
            if options.data.gfx == "oryx":
                self.items_icons.append(get_tile(item.biome_data["wall"]))
            else:
                self.items_icons.append("#")
            quest = choice(item.biome_data["quests"])
            if quest == "rescue":
                npc = choice(item.biome_data["npcs"])
            else:
                npc = choice(item.biome_data["monsters"])
            quest_title = quest.capitalize() + ":" + " " + npc.capitalize()
            self.sub_items[name] = [quest_title]

    def show(self):
        output = self.owner.show(self)
        if not output:
            self.event = None
        else:
            self.event = "level_change"
            output.params = self.data[self.owner.sel_index]
            self.owner.handle_output(output)
