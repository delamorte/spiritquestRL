class Camera:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move_camera(self, target_x, target_y, map_width, map_height):
        x = target_x - int(self.width / 2)
        y = target_y - int(self.height / 2)

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > map_width - self.width:
            x = map_width - self.width
        if y > map_height - self.height:
            y = map_height - self.height
        self.x, self.y = x, y

    def get_coordinates(self, map_x, map_y):
        x, y = map_x - self.x, map_y - self.y

        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return -1, -1
        return x, y
