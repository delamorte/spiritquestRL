from random import choice

from bearlibterminal import terminal as blt

import options
from components.menus.menu_item import MenuItem
from map_gen.tilemap import get_tile


class ChooseLevel:
    def __init__(self, name="choose_level", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = MenuItem("[color=white]Choose your destination...")
        self.items = []
        self.sub_menu = sub_menu
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        for item in self.data:
            name = item.title
            if options.data.gfx == "oryx":
                tile = get_tile(item.biome_data["wall"])
                icon = tile
            else:
                icon = None
            quest = item.quest
            if quest == "rescue":
                npc = item.quest_npc
            else:
                npc = choice(item.biome_data["monsters"])
            quest_title = "\n" + quest.capitalize() + ":" + " " + npc.capitalize()

            text_lines = name + quest_title
            menu_item = MenuItem(name, text_lines, icon)
            self.items.append(menu_item)

    def show(self):
        output = self.owner.show(self)
        if not output:
            self.event = None
        else:
            self.event = "level_change"
            output.params = self.data[self.owner.sel_index]
            self.owner.handle_output(output)
