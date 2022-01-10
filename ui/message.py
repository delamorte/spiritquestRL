class Message:
    def __init__(self, msg=None, color=None, style=None, extend_line=False, clear_buffer=False):
        self.msg = msg
        self.color = color
        self.style = style
        self.extend_line = extend_line
        self.clear_buffer = clear_buffer
        self.stacked = 1
        self.colorize()

    def colorize(self):
        if self.style:
            colors = {
                "miss": "gray",
                "skill_use": "orange",
                "status_effect": "green",
                "attack": "lighter red",
                "question": "yellow",
                "death": "red",
                "level_up": "lighter blue",
                "xtra": "amber"
            }
            self.color = colors[self.style]

        self.msg = "[color={0}]{1}".format(self.color, self.msg)
