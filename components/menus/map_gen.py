from bearlibterminal import terminal as blt


class MapGen:
    def __init__(self, name="map_gen", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.sub_menu = sub_menu
        self.heading = None
        self.sub_heading = None
        self.items = ["messy_bsp", "cellular", "random_walk", "room_addition"]
        self.items_icons = []
        self.sub_items = {}
        self.margin_x = 0
        self.margin_y = 1
        self.align = blt.TK_ALIGN_CENTER
        self.event = event
        self.refresh()

    def refresh(self):
        pass

    def show(self,):
        output = self.owner.show(self)
        if not output and self.sub_menu:
            self.event = "show_prev_menu"
        else:
            self.event = None
            self.owner.handle_output(output)
