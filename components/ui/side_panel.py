class SidePanel:
    def __init__(self, x, y, w, h):
        self.owner = None
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h
        self.dx = 0
        self.dy = 0
        self.offset_x = 0
        self.offset_y = 0
        self.offset_w = 0
        self.offset_h = 0
        self.offset_x2 = 0
        self.offset_y2 = 0
        self.border = 1
        self.x_margin = 4

    def draw(self):
        self.owner.owner.render_functions.draw_ui(self)

    def draw_content(self):
        self.owner.owner.render_functions.draw_side_panel_content()

    def update(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h

    def update_offset(self, offset_x, offset_y):
        self.offset_x = self.x * offset_x
        self.offset_y = self.y * offset_y
        self.offset_w = self.w * offset_x
        self.offset_h = self.h * offset_y
        self.offset_x2 = self.offset_x + self.offset_w
        self.offset_y2 = self.offset_y + self.offset_h
