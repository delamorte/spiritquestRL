from bearlibterminal import terminal as blt

from components.menus.menu_item import MenuItem


class LevelUp:
    def __init__(self, name="level_up", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.sub_menu = sub_menu
        self.heading = MenuItem("[color=white]You have gained more wisdom. You feel a stronger bond with one particular " \
                       "spirit... ")
        self.items = []
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        animals = self.data.player.char
        exclude = self.data.player.max_lvl_avatars
        avatars = {x: animals[x] for x in animals if x not in exclude}
        if not avatars:
            self.items.append("Alas, you have no bonds to strengthen at the moment...")
            return
        row_3 = ""
        for (k, v) in avatars.items():
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

                row_3 = "\n Learns new skill: {0}".format(", ".join(next_learnable_abilities[:potential_levels]))
            else:
                next_avatar_lvl = avatar_lvl

            row_1 = " LVL: {0}, EXP: {1}/{2}".format(avatar_lvl, str(self.data.player.char_exp[k]), exp_interval)
            row_2 = "\n -> LVL: {0}, EXP: {1}/{2}".format(next_avatar_lvl,
                                                        str(potential_exp),
                                                        next_exp_interval)
            icon = v
            text_lines = row_1 + row_2 + row_3
            menu_item = MenuItem(k, text_lines, icon)
            self.items.append(menu_item)

    def show(self):
        self.refresh()
        output = self.owner.show(self)
        results = None
        if output:
            results = self.data.player.handle_avatar_exp(output.params)
            self.owner.handle_output(output)
        return results
