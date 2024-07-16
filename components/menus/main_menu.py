from bearlibterminal import terminal as blt

import options
from components.menus.menu_item import MenuItem


class MainMenu:
    def __init__(self, name="main", title_screen=False, data=None, sub_menu=False):
        self.owner = None
        self.name = name
        self.title_screen = title_screen
        self.data = data
        self.align = blt.TK_ALIGN_CENTER
        self.header = MenuItem("[color=white]Spirit Quest RL")
        self.items = [MenuItem("New game"), MenuItem("Exit")]
        if options.data.debug:
            self.items.insert(0, MenuItem("Map generator"))
        self.sub_menu = sub_menu

    def refresh(self):
        self.owner.refresh()

    def show(self):
        if not self.title_screen:
            if not [x for x in self.items if x.value == "Resume game"]:
                self.items.insert(0, MenuItem("Resume game"))
        output = self.owner.show(self)
        if output:
            self.owner.handle_output(output)

