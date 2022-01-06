from bearlibterminal import terminal as blt
from math import floor

from components.ui.message_panel import MessagePanel
from components.ui.side_panel import SidePanel
from components.ui.viewport import Viewport


class UIElements:
    def __init__(self):
        self.owner = None
        self.render_functions = None
        self.elements = []
        self.ui_offset_y = 3
        self.ui_offset_x = 4
        self.msg_panel = None
        self.side_panel = None
        self.viewport = None

        self.init_ui()

    def init_ui(self):
        screen_w = blt.state(floor(blt.TK_WIDTH))
        screen_h = blt.state(floor(blt.TK_HEIGHT))
        w = floor(screen_w / self.ui_offset_x)
        h = floor(screen_h / self.ui_offset_y)

        # Side panel
        side_panel_w = 10
        side_panel_x = w - side_panel_w
        if not self.side_panel:
            self.side_panel = SidePanel(side_panel_x, 0, side_panel_w-1, h)
            self.side_panel.owner = self
            self.elements.append(self.side_panel)
            self.side_panel.update_offset(self.ui_offset_x, self.ui_offset_y)
        else:
            self.side_panel.update(side_panel_x, 0, side_panel_w-1, h)
            self.side_panel.update_offset(self.ui_offset_x, self.ui_offset_y)

        if not self.viewport:
            self.viewport = Viewport(0, 0, w-side_panel_w, h-5)
            self.viewport.owner = self
            self.elements.append(self.viewport)
        else:
            self.viewport.update_borders(w-side_panel_w, h-5)

        if not self.msg_panel:
            self.msg_panel = MessagePanel(0, self.viewport.h + 1, w - side_panel_w, h-self.viewport.h)
            self.msg_panel.owner = self
            self.elements.append(self.msg_panel)
        else:
            self.msg_panel.update(0, self.viewport.h + 1, w - side_panel_w, h-self.viewport.h)

        # Calculate real viewport width and height with tile size offsets
        viewport_w = (w - side_panel_w) * self.ui_offset_x - (self.ui_offset_x + 1)
        viewport_h = (h - 5) * self.ui_offset_y - (self.ui_offset_y + 1)
        self.viewport.update(viewport_w, viewport_h)

    def draw(self):
        for element in self.elements:
            self.render_functions.draw_ui(element)
