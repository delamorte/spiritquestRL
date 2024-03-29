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
        self.sub_heading = None
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
        exclude = self.data.player.max_lvl_avatars
        avatars = {x: animals[x] for x in animals if x not in exclude}
        if not avatars:
            self.items.append("Alas, you have no bonds to strengthen at the moment...")
            return
        exp_3 = ""
        for (k, v) in avatars.items():
            self.items.append(k)
            self.items_icons.append(v)
            if k not in self.data.player.avatar:
                continue
            avatar = self.data.player.avatar[k]
            next_learnable_abilities = self.data.abilities.learnable[k]
            avatar_lvl = avatar.level
            exp_intervals = self.data.player.avatar_exp_lvl_intervals
            exp_interval = exp_intervals[max(0, avatar_lvl - 1)]
            current_avatar_exp = self.data.player.char_exp[k]
            potential_exp = current_avatar_exp + self.data.player.avatar_exp_to_spend
            potential_levels = 0

            if avatar_lvl >= len(exp_intervals):
                exp_interval = "MAX"
            else:
                for interval in exp_intervals[avatar_lvl:]:
                    if potential_exp >= interval:
                        potential_levels += 1
                    else:
                        break
            if avatar_lvl + potential_levels >= len(exp_intervals):
                next_exp_interval = "MAX"
            else:
                next_exp_interval = exp_intervals[min(len(exp_intervals) - 1, avatar_lvl + potential_levels)]

            if potential_levels > 0:
                next_avatar_lvl = min(len(exp_intervals) - 1, avatar_lvl + potential_levels)

                exp_3 = " Learns new skill: {0}".format(", ".join(next_learnable_abilities[:potential_levels]))
            else:
                next_avatar_lvl = avatar_lvl

            exp = " LVL: {0}, EXP: {1}/{2}".format(avatar_lvl, str(self.data.player.char_exp[k]), exp_interval)
            exp_2 = " -> LVL: {0}, EXP: {1}/{2}".format(next_avatar_lvl,
                                                        str(potential_exp),
                                                        next_exp_interval)

            self.sub_items[k] = [exp, exp_2, exp_3]

    def show(self):
        self.refresh()
        output = self.owner.show(self)
        results = None
        if output:
            results = self.data.player.handle_avatar_exp(output.params)
            self.owner.handle_output(output)
        return results
