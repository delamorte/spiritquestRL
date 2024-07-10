from map_gen.tilemap import get_color


class MenuItem:
    def __init__(self, value=None, text_lines=None, icon=None, color=None, heading=False, dialogue=False):
        self.value = value
        self.color = color
        self.heading = heading
        self.dialogue = dialogue
        if self.dialogue:
            self.text_lines = "[color=light amber]{0}: \n[color=default]".format(self.value)
        elif not text_lines:
            self.text_lines = value
        else:
            self.text_lines = text_lines
        self.icon = icon

    def append(self, line):
        self.text_lines += "\n" + line

    def reset(self):
        if self.dialogue:
            self.text_lines = "[color=light amber]{0}: \n[color=default]".format(self.value)
        else:
            self.text_lines = self.value

    def get_text(self):
        if not self.icon:
            return self.text_lines
        else:
            icon_color = get_color(self.value)
            if icon_color is None or icon_color == "default":
                icon_color = "amber"
            icon_str = "[color={0}][U+{1}][color={2}]\n".format(icon_color, hex(self.icon), self.color)
            text_lines = icon_str + self.text_lines
            return text_lines
