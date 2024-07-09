from map_gen.tilemap import get_color


class MenuItem:
    def __init__(self, value=None, item_str=None, icon=None, color=None):
        self.value = value
        self.color = color
        if not item_str:
            self.item_str = value
        else:
            self.item_str = item_str
        self.icon = icon
        # if icon:
        #     icon_color = get_color(value)
        #     if icon_color is None or icon_color == "default":
        #         icon_color = "amber"
        #     icon_str = "[color={0}][U+{1}][color={2}]\n".format(icon_color, hex(icon), self.color)
        #     self.item_str = icon_str + item_str

    def get_text(self):
        if not self.icon:
            return self.item_str
        else:
            icon_color = get_color(self.value)
            if icon_color is None or icon_color == "default":
                icon_color = "amber"
            icon_str = "[color={0}][U+{1}][color={2}]\n".format(icon_color, hex(self.icon), self.color)
            item_str = icon_str + self.item_str
            return item_str
