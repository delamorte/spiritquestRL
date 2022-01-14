import re


class Message:
    def __init__(self, msg=None, color=None, style=None, extend_line=False, clear_buffer=False):
        self.msg = msg
        self.color = color
        self.style = style
        self.extend_line = extend_line
        self.clear_buffer = clear_buffer
        self.stacked = 1
        if self.style:
            self.colorize()

    def colorize(self):

        colors = {
            "miss": "gray",
            "skill_use": "orange",
            "status_effect": "green",
            "attack": "lighter red",
            "question": "yellow",
            "death": "red",
            "level_up": "lighter blue",
            "xtra": "amber",
            "dialog": "light azure"
        }
        self.color = colors[self.style]
        regexex_msg = re.sub(r'\[.*?\]', '', self.msg)
        self.msg = "[color={0}]{1}[color=default]".format(self.color, regexex_msg)
