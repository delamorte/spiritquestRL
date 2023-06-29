from random import choice, shuffle

from bearlibterminal import terminal as blt


class DialogueMenu:
    def __init__(self, name="dialogue", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.heading = "[color=white]{0}: ".format(self.data.dialogue_json["actor"])
        self.sub_heading = None
        self.items = []
        self.items_icons = []
        self.sub_items = {}
        self.sub_menu = sub_menu
        self.margin_x = 6
        self.margin_y = 1
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.options = {}
        self.prev_state = None
        self.next_state = None
        # self.refresh()

    def refresh(self):
        self.items = []
        self.items_icons = []
        self.sub_items = {}

        line_1 = choice(self.data.dialogue_json["dialogue"]["idle"])
        line_2 = choice(self.data.dialogue_json["dialogue"]["prompts"][self.data.prompt_state])

        self.sub_heading = "{0} \n {1}".format(line_1, line_2)

        for item in self.data.dialogue_json["dialogue"]["answers"][self.data.prompt_state]:
            for option in item["choices"]:
                self.options[option] = item["go_to"]
                self.items.append(option)
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
                output.sub_menu = True
            results = output.messages
            self.owner.handle_output(output)
        return results
