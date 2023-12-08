from bearlibterminal import terminal as blt

import options


class MainMenu:
    def __init__(self, name="main", title_screen=False, data=None, sub_menu=False):
        self.owner = None
        self.name = name
        self.title_screen = title_screen
        self.data = data
        self.margin_x = 0
        self.margin_y = 1
        self.align = blt.TK_ALIGN_CENTER
        self.heading = "[color=white]Spirit Quest RL"
        self.sub_heading = None
        self.items = ["New game", "Exit"]
        if options.data.debug:
            self.items.insert(0, "Map generator")
        self.items_icons = []
        self.sub_items = {}
        self.sub_menu = sub_menu

    def refresh(self):
        self.owner.refresh()

    def show(self):
        if not self.title_screen:
            if "Resume game" not in self.items:
                self.items.insert(0, "Resume game")
        output = self.owner.show(self)
        if output:
            self.owner.handle_output(output)

