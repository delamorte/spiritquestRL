from bearlibterminal import terminal as blt
from math import floor
import variables

def init_ui():

    screen_w = blt.state(floor(blt.TK_WIDTH))
    screen_h = blt.state(floor(blt.TK_HEIGHT))

    w = floor(screen_w / variables.ui_offset_x)
    h = floor(screen_h / variables.ui_offset_y - 5)

    msg_panel = Panel(1, h + 1, w - 1, h + 4)
    msg_panel_borders = Panel(0, h, w, h + 5)
    screen_borders = Panel(0, 0, w, h)

    viewport_x = w * variables.ui_offset_x - (variables.ui_offset_x + 1)
    viewport_y = h * variables.ui_offset_y - (variables.ui_offset_y + 1)
    variables.viewport_x = viewport_x
    variables.viewport_y = viewport_y
    return msg_panel, msg_panel_borders, screen_borders

class Panel:

    def __init__(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
