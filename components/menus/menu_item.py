import re

from map_gen.tilemap import get_color


class MenuItem:
    def __init__(self, value=None, text_lines=None, icon=None, color=None, header=False, dialogue=False,
                 npc=None):
        self.value = value
        self.color = color
        self.header = header
        self.dialogue = dialogue
        self.npc = npc
        if self.dialogue:
            self.text_lines = "[color=light amber]{0}: \n[color=default]".format(self.value)
        elif not text_lines:
            self.text_lines = value
        else:
            self.text_lines = text_lines
        self.icon = icon
        if self.npc:
            self.replace_dict = {
                '{actor_name}': self.npc.name.capitalize(),
                '{actor_home}': self.npc.home.capitalize(),
                '{actor_action}': self.npc.action.capitalize()
            }
        else:
            self.replace_dict = None
        self.text_lines = self.process_text(self.text_lines)

    def append(self, line):
        processed_line = self.process_text(line)
        self.text_lines += "\n" + processed_line

    def reset(self):
        if self.dialogue:
            self.text_lines = "[color=light amber]{0}: \n[color=default]".format(self.value)
        else:
            self.text_lines = self.value

    def process_text(self, text):
        content_to_replace = re.findall(r'\{.*?}', text)
        for word in content_to_replace:
            text = text.replace(word, self.replace_dict[word])
        return text

    def get_text(self):
        if not self.icon and self.npc:
            text_lines = self.process_text(self.text_lines)
            return text_lines
        elif self.icon:
            icon_color = get_color(self.value)
            if icon_color is None or icon_color == "default":
                icon_color = "amber"
            icon_str = "[color={0}][U+{1}][color={2}]\n".format(icon_color, hex(self.icon), self.color)
            text_lines = icon_str + self.text_lines
            return text_lines
        else:
            return self.text_lines
