from math import floor

from bearlibterminal import terminal as blt

from components.ui.message_panel import MessagePanel
from components.ui.side_panel import SidePanel
from components.ui.viewport import Viewport
from map_gen.tilemap import get_tile_variant, get_color


class UIElements:
    def __init__(self):
        self.owner = None
        self.color = get_color("ui_block")
        self.tile_horizontal = get_tile_variant("ui_block", facing=0, no_ascii=True)
        self.tile_vertical = get_tile_variant("ui_block", facing=2, no_ascii=True)
        self.tile_ne = get_tile_variant("ui_block", facing=1, no_ascii=True)
        self.tile_se = get_tile_variant("ui_block", facing=3, no_ascii=True)
        self.tile_sw = get_tile_variant("ui_block", facing=5, no_ascii=True)
        self.tile_nw = get_tile_variant("ui_block", facing=7, no_ascii=True)
        self.screen_w = blt.state(floor(blt.TK_WIDTH))
        self.screen_h = blt.state(floor(blt.TK_HEIGHT))
        self.elements = []
        self.offset_y = 3
        self.offset_x = 4
        self.msg_panel = None
        self.side_panel = None
        self.viewport = None

        self.init_ui()

    def init_ui(self):

        w = floor(self.screen_w / self.offset_x)
        h = floor(self.screen_h / self.offset_y)

        # Side panel
        side_panel_w = 10
        side_panel_x = w - side_panel_w

        self.side_panel = SidePanel(side_panel_x, 0, side_panel_w-1, h-1)
        self.side_panel.owner = self
        self.elements.append(self.side_panel)
        self.side_panel.update_offset(self.offset_x, self.offset_y)

        self.viewport = Viewport(0, 0, w-side_panel_w-1, h-6)
        self.viewport.owner = self
        self.elements.append(self.viewport)
        self.viewport.update_offset(self.offset_x, self.offset_y)

        self.msg_panel = MessagePanel(0, self.viewport.h+1, self.viewport.w, h-self.viewport.h)
        self.msg_panel.owner = self
        self.elements.append(self.msg_panel)
        self.msg_panel.update_offset(self.offset_x, self.offset_y)

    def draw(self):
        for element in self.elements:
            self.owner.render_functions.draw_ui(element)
