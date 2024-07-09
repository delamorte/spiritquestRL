from random import choice, shuffle

from bearlibterminal import terminal as blt

from components.menus.menu_item import MenuItem


class DialogueMenu:
    def __init__(self, name="dialogue", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=light amber]{0}: \n[color=default]".format(self.data.dialogue_json["actor"])
        self.items = []
        self.sub_menu = sub_menu
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.options = {}
        self.prev_state = None
        self.next_state = None
        self.first_interaction = True
        # self.refresh()

    def refresh(self):
        if not self.first_interaction and self.data.prompt_state is None:
            return
        self.items = []
        self.options = {}
        line_1 = ""
        if self.first_interaction:
            line_1 = choice(self.data.dialogue_json["dialogue"]["idle"])
            self.first_interaction = False

        line_2 = choice(self.data.dialogue_json["dialogue"]["prompts"][self.data.prompt_state])

        self.heading += "\n{0}\n\n{1}\n".format(line_1, line_2)

        for item in self.data.dialogue_json["dialogue"]["answers"][self.data.prompt_state]:
            for option in item["choices"]:
                self.options[option] = item["go_to"]
                menu_item = MenuItem(option)
                self.items.append(menu_item)
        shuffle(self.items)

    def show(self):
        self.refresh()
        results = []
        output = self.owner.show(self)
        if output:
            if output.params in self.options:
                self.prev_state = self.data.prompt_state
                self.next_state = self.options[output.params]
                self.data.prompt_state = self.next_state
                if self.next_state is None:
                    output.sub_menu = False
                else:
                    output.sub_menu = True
            results = output.messages
            self.owner.handle_output(output)
        return results
