from bearlibterminal import terminal as blt


class AvatarInfo:
    def __init__(self, name="avatar_info", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.sub_menu = sub_menu
        self.heading = "[color=white]The following spirits have awakened within you.."
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.margin_x = 6
        self.margin_y = 6
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        animals = self.data.player.char
        exclude = {"player"}
        avatars = {x: animals[x] for x in animals if x not in exclude}
        for (k, v) in avatars.items():
            self.items.append(k)
            self.items_icons.append(v)
            exp = " EXP: " + str(self.data.player.char_exp[k])
            self.sub_items[k] = [exp]

    def show(self):
        self.refresh()
        output = self.owner.show(self)
        if output:
            self.owner.handle_output(output)
