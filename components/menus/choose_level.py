from map_objects import tilemap


class ChooseLevel:
    def __init__(self, name="choose_level", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]Choose your destination..."
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
        for item in self.data:
            name = item["title"]
            self.items.append(name)
            if tilemap.data.tileset == "oryx":
                self.items_icons.append(0xE000 + 399)
            else:
                self.items_icons.append("#")
            self.sub_items[name] = ["Rescue: Blacksmith"]

    def show(self):
        output = self.owner.show(self)
        if not output:
            self.event = None
        else:
            self.event = "level_change"
            output.params = self.data[self.owner.sel_index]
            self.owner.handle_output(output)
