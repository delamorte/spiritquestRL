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
        for item in self.data:
            name = item["title"]
            self.items.append(name)
            self.items_icons.append(0xE000 + 399)
            self.sub_items[name] = ["Rescue: Blacksmith"]

    def refresh(self):
        self.owner.refresh(self.heading)

    def show(self):
        output = self.owner.show(self)
        if output:
            self.event = "go_to_level"
            output = self.data[self.owner.sel_index]
            self.owner.handle_output(output)
