from math import ceil, floor

import settings


class Camera:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_width = int(floor(settings.viewport_w / settings.ui_offset_x + 2))
        self.max_height = int(floor(settings.viewport_h / settings.ui_offset_y + 2))
        self.width = self.max_width
        self.height = self.max_height
        self.offset = int(settings.ui_size) / int(settings.tile_height)
        self.bound_x = ceil(self.offset)
        self.bound_y = ceil(self.offset)
        self.bound_x2 = self.width - ceil(self.offset)
        self.bound_y2 = self.height - ceil(self.offset)

    def move_camera(self, target_x, target_y, map_width, map_height):
        
        if map_width <= self.width:
            self.width = map_width
        else:
            self.width = self.max_width
        if map_height <= self.height:
            self.height = map_height
        else:
            self.height = self.max_height

        self.update_boundaries()

        x = target_x - int(self.width / 2)
        y = target_y - int(self.height / 2)

        if x < 0:
            x = -int(self.offset / 2)
        if y < 0:
            y = -int(self.offset / 2)
        if x > map_width - self.width:
            x = map_width - self.width + int(self.offset / 2)
        if y > map_height - self.height:
            y = map_height - self.height + int(self.offset / 2)
        self.x, self.y = x, y

    def get_coordinates(self, map_x, map_y):
        x, y = map_x - self.x, map_y - self.y

        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return -1, -1
        return x, y

    def update_boundaries(self):
        self.bound_x = ceil(self.offset)
        self.bound_y = ceil(self.offset)
        self.bound_x2 = self.width - ceil(self.offset)
        self.bound_y2 = self.height - ceil(self.offset)
