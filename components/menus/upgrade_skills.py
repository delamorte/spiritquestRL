from bearlibterminal import terminal as blt
from data import json_data
from map_objects import tilemap
from ui.message import Message


class UpgradeSkills:
    def __init__(self, name="upgrade_skills", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]The following abilities have awakened within you..."
        self.sub_heading = None
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.sub_menu = sub_menu
        self.margin_x = 6
        self.margin_y = 7
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.refresh()

    def refresh(self):
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        abilities = self.data.abilities
        skill_points = self.data.player.skill_points
        self.sub_heading = "[color=yellow]You have {0} skill points".format(skill_points)

        for skill in abilities.items:
            self.items.append(skill.name)
            self.items_icons.append(skill.icon)
            description = "[color=white]{0}".format(skill.get_description())
            next_rank_description = ""
            upgradeable = skill.rank < skill.max_rank
            if upgradeable:
                next_rank_description =\
                    "[color=lighter blue]Rank {0}[color=white] -> {1}".format(skill.rank+2,
                                                                              skill.get_description(rank=skill.rank+1))

            self.sub_items[skill.name] = [skill.description, description, next_rank_description]

        for skill in abilities.unlocked:
            self.items.append(skill.name)
            self.items_icons.append(skill.icon)
            learn_str = "[color=lighter yellow]New skill[color=white]"
            description = skill.get_description()

            self.sub_items[skill.name] = [learn_str, skill.description, description]

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
