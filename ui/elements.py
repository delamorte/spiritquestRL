from bearlibterminal import terminal as blt
from math import floor
import settings


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
        w = floor(screen_w / settings.ui_offset_x)
        h = floor(screen_h / settings.ui_offset_y)

        side_panel_w = 10

        self.screen_borders = Panel(0, 0, w-side_panel_w, h-5)
        self.side_panel_borders = Panel(w-side_panel_w, 0, side_panel_w-1, h)

        self.msg_panel_borders = Panel(0, self.screen_borders.h+1, w-side_panel_w, h-(self.screen_borders.h))
        self.msg_panel = Panel(1, self.msg_panel_borders.y+1, self.msg_panel_borders.w-1, self.msg_panel_borders.h-1)

        settings.viewport_w = (w - side_panel_w) * settings.ui_offset_x - (settings.ui_offset_x + 1)
        settings.viewport_h = (h - 5) * settings.ui_offset_y - (settings.ui_offset_y + 1)

        settings.viewport_center_x = int(settings.viewport_w / 2)
        settings.viewport_center_y = int(settings.viewport_h / 2)


class Panel:

    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h

    def new_popup(self):
        self.x = settings.viewport_center_x - 20
        self.y = settings.viewport_center_y - 10
        self.w = 30
        self.h = 10
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
