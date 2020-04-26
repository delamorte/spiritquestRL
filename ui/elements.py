from bearlibterminal import terminal as blt
from math import floor
import variables


class UIElements:
    def __init__(self):

        self.msg_panel = None
        self.msg_panel_borders = None
        self.screen_borders = None
        self.side_panel_borders = None
        self.viewport_x = None
        self.viewport_y = None
        self.viewport = None

        self.init_ui()

    def init_ui(self):
        screen_w = blt.state(floor(blt.TK_WIDTH))
        screen_h = blt.state(floor(blt.TK_HEIGHT))
        w = floor(screen_w / variables.ui_offset_x)
        h = floor(screen_h / variables.ui_offset_y)

        side_panel_w = 10

        self.screen_borders = Panel(0, 0, w-side_panel_w, h-5)
        self.side_panel_borders = Panel(w-side_panel_w, 0, side_panel_w-1, h)

        self.msg_panel_borders = Panel(0, self.screen_borders.h, w-side_panel_w, h-(self.screen_borders.h))
        self.msg_panel = Panel(1, self.msg_panel_borders.y+1, self.msg_panel_borders.w-1, self.msg_panel_borders.h-1)

        variables.viewport_w = (w-side_panel_w) * variables.ui_offset_x - (variables.ui_offset_x + 1)
        variables.viewport_h = (h-5) * variables.ui_offset_y - (variables.ui_offset_y + 1)


class Panel:

    def __init__(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
