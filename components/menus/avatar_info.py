from bearlibterminal import terminal as blt

from components.menus.menu_item import MenuItem


class AvatarInfo:
    def __init__(self, name="avatar_info", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.sub_menu = sub_menu
        self.heading = "[color=white]The following spirits have awakened within you.."
        self.items = []
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        animals = self.data.player.char
        exclude = {"player"}
        avatars = {x: animals[x] for x in animals if x not in exclude}
        for (k, v) in avatars.items():
            extra = "\n EXP: " + str(self.data.player.char_exp[k])
            item_str = k + extra
            icon = v
            menu_item = MenuItem(k, item_str, icon)
            self.items.append(menu_item)

    def show(self):
        self.refresh()
        output = self.owner.show(self)
        if output:
            self.owner.handle_output(output)
