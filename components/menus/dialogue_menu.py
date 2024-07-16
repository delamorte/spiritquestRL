from random import choice

from bearlibterminal import terminal as blt

from components.menus.menu_item import MenuItem
from game_states import NpcStates


class DialogueMenu:
    def __init__(self, name="dialogue", data=None, sub_menu=False, event=None):
        self.owner = None
        self.title_screen = False
        self.name = name
        self.data = data
        self.header = MenuItem(self.data.npc.name.capitalize(), dialogue=True, npc=self.data.npc)
        self.items = []
        self.sub_menu = sub_menu
        self.align = blt.TK_ALIGN_LEFT
        self.event = event
        self.options = {}
        self.prev_choice = None
        self.next_choice = None
        # self.refresh()

    def refresh(self):
        self.header.reset()
        if self.data.npc.state == NpcStates.IDLE and self.data.current_choice is None:
            return
        elif self.data.npc.state == NpcStates.SHOP:
            print("TODO: open shop menu")
            self.data.npc.set_state(self.data.npc.prev_state)
        self.items = []
        self.options = {}

        line_1 = choice(self.data.dialogue_json["dialogue"][self.data.npc.state.value])
        self.header.append(line_1)
        dialogue_state = self.data.npc.state.value

        if self.data.current_choice:
            line_2 = choice(self.data.dialogue_json["dialogue"]["choices"][self.data.current_choice])
            self.header.append(line_2)
            dialogue_state = self.data.current_choice

        for item in self.data.dialogue_json["dialogue"]["player"][dialogue_state]:
            for option in item["choices"]:
                self.options[option] = {}
                self.options[option]["choice"] = item["go_to"]
                self.options[option]["state"] = item["set_state"] if "set_state" in item.keys() else None
                menu_item = MenuItem(option, npc=self.data.npc)
                self.items.append(menu_item)

    def show(self):
        self.refresh()
        results = []
        output = self.owner.show(self)
        if output:
            if output.params in self.options:
                self.prev_choice = self.data.current_choice
                self.next_choice = self.options[output.params]["choice"]
                state = self.options[output.params]["state"]
                if state:
                    self.data.npc.set_state(state)
                self.data.current_choice = self.next_choice
                if self.next_choice is None:
                    output.sub_menu = False
                else:
                    output.sub_menu = True
            results = output.messages
            self.owner.handle_output(output)
        return results
