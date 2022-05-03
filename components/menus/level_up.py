from bearlibterminal import terminal as blt


class LevelUp:
    def __init__(self, name="level_up", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.sub_menu = sub_menu
        self.heading = "[color=white]You have gained more wisdom. You feel a stronger bond with one particular " \
                       "spirit... "
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
            if k not in self.data.player.avatar:
                continue
            avatar = self.data.player.avatar[k]
            avatar_lvl = avatar.level
            exp_intervals = self.data.player.avatar_exp_lvl_intervals
            if avatar_lvl >= len(exp_intervals):
                exp_interval = "MAX"
                next_exp_interval = "MAX"
            else:
                exp_interval = exp_intervals[min(0, avatar_lvl - 1)]
                next_exp_interval = exp_intervals[min(0, avatar_lvl)]

            potential_exp = self.data.player.char_exp[k] + self.data.player.avatar_exp_to_spend
            if exp_intervals[-1] > potential_exp >= exp_interval:
                next_avatar_lvl = avatar_lvl + 1
                exp_3 = " Learns new skill"
            else:
                next_avatar_lvl = avatar_lvl
                exp_3 = ""

            exp = " LVL: {0}, EXP: {1}/{2}".format(avatar_lvl, str(self.data.player.char_exp[k]), exp_interval)
            exp_2 = " -> LVL: {0}, EXP: {1}/{2}".format(next_avatar_lvl,
                                                        str(potential_exp),
                                                        next_exp_interval)
            self.sub_items[k] = [exp, exp_2, exp_3]

    def show(self):
        self.refresh()
        output = self.owner.show(self)
        if output:
            self.data.player.handle_level_up(output.params)
            self.owner.handle_output(output)
