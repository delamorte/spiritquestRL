from bearlibterminal import terminal as blt

from components.menus.menu_item import MenuItem
from ui.message import Message


class UpgradeSkills:
    def __init__(self, name="upgrade_skills", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.header = MenuItem("[color=white]The following abilities have awakened within you...")
        self.items = []
        self.sub_menu = sub_menu
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        abilities = self.data.abilities
        skill_points = self.data.player.skill_points
        self.header.append("[color=yellow]You have {0} skill points".format(skill_points))

        for skill in abilities.items:
            icon = skill.icon
            text_lines = skill.name
            description = "\n [color=white]{0}".format(skill.get_description())
            next_rank_description = ""
            upgradeable = skill.rank < skill.max_rank
            if upgradeable:
                next_rank_description =\
                    "\n [color=lighter blue]Rank {0}[color=white] -> {1}".format(skill.rank+2,
                                                                              skill.get_description(rank=skill.rank+1))

            text_lines += "\n" + skill.description + description + next_rank_description
            menu_item = MenuItem(skill.name, text_lines, icon)
            self.items.append(menu_item)

        for skill in abilities.unlocked:
            icon = skill.icon
            text_lines = skill.name
            learn_str = "\n [color=lighter yellow]New skill[color=white]"
            description = skill.get_description()

            text_lines += "\n" + learn_str + "\n" + skill.description + "\n" + description
            menu_item = MenuItem(skill.name, text_lines, icon)
            self.items.append(menu_item)

    def show(self):
        self.refresh()
        results = []
        output = self.owner.show(self)
        if output:
            results = output.messages
            self.owner.handle_output(output)
        return results

    def spend_points(self, output):
        results = []
        if output:
            if self.data.player.skill_points > 0:
                results = self.data.abilities.learn_or_rank_up(output.params)
            else:
                results.append(Message(msg="You have no skill points..."))
            output.params = None
            output.messages.extend(results)
            output.menu_actions_left = self.data.player.skill_points > 0
        self.refresh()
        return output
