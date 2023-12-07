from bearlibterminal import terminal as blt


class DebugMap:
    def __init__(self, name="debug_map", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.sub_menu = sub_menu
        self.heading = None
        self.sub_heading = None
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.margin_x = 6
        self.margin_y = 6
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        pass

    def show(self, draw_map):
        if isinstance(self.data, str):
            blank_map = True
        else:
            blank_map = False

        draw_map(params=self.data, blank_map=blank_map)

        output = self.owner.show(self)
        if not output and self.sub_menu:
            self.event = "show_prev_menu"
        if output:
            self.owner.handle_output(output)
