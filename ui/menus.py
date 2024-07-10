from math import ceil

from bearlibterminal import terminal as blt

from components.menus.avatar_info import AvatarInfo
from components.menus.choose_animal import ChooseAnimal
from components.menus.choose_level import ChooseLevel
from components.menus.debug_map import DebugMap
from components.menus.dialogue_menu import DialogueMenu
from components.menus.level_up import LevelUp
from components.menus.map_gen import MapGen
from components.menus.upgrade_skills import UpgradeSkills
from game_states import GameStates


class MessageList(object):
    def __init__(self):
        self.total_height = 1
        self.texts = []
        self.heights = []

    def update_heights(self, width):
        self.heights = [blt.measure(text.get_text(), width)[1] for text in self.texts]
        # recompute total height, including the blank lines between messages
        self.total_height = sum(self.heights) + len(self.texts) - 1

    def append(self, message):
        self.texts.append(message)

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, key):
        return self.texts[key], self.heights[key]


class FrameWithScrollbar(object):
    def __init__(self, contents):
        self.offset = 0
        self.width = 0
        self.height = 0
        self.scrollbar_height = 0
        self.scrollbar_column = 0
        self.scrollbar_offset = 0
        self.left = self.top = self.width = self.height = 0
        self.contents = contents

    def update_geometry(self, left, top, width, height):
        # Save current scroll position
        current_offset_percentage = self.offset / self.contents.total_height

        # Update frame dimensions
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        # Calculate new message list height
        self.contents.update_heights(width)

        # Scrollbar
        #self.scrollbar_height = 1
        self.scrollbar_height = min(
            int(ceil(self.height * self.height / self.contents.total_height)), self.height)

        # Try to recover scroll position
        self.offset = int(self.contents.total_height *
                          current_offset_percentage)
        self.offset = min(
            self.offset, self.contents.total_height - self.height)
        if self.contents.total_height <= self.height:
            self.offset = 0

    def scroll_to_pixel(self, py):
        py -= self.top * blt.state(blt.TK_CELL_HEIGHT)
        factor = py / (self.height * blt.state(blt.TK_CELL_HEIGHT))
        self.offset = int(self.contents.total_height * factor)
        self.offset = max(
            0, min(self.contents.total_height - self.height, self.offset))

    def scroll(self, dy):
        self.offset = max(
            0, min(self.contents.total_height - self.height, self.offset + dy))

    def draw(self):
        # Frame background
        blt.layer(0)
        blt.color("transparent")
        blt.clear_area(self.left, self.top, self.width, self.height)

        # Scroll bar
        blt.bkcolor("transparent")
        blt.clear_area(self.left + self.width, self.top, 1, self.height)
        #blt.bkcolor("default")
        blt.color("dark orange")
        self.scrollbar_column = self.left + self.width
        self.scrollbar_offset = int(
            (self.top + (self.height - self.scrollbar_height) * (
                self.offset / (self.contents.total_height - self.height))) *
            blt.state(blt.TK_CELL_HEIGHT))
        for i in range(self.scrollbar_height):
            blt.put_ext(self.scrollbar_column, i, 0,
                        self.scrollbar_offset, 0x2588)

class Menus:
    def __init__(self, main_menu=None, choose_animal=None, choose_level=None, avatar_info=None,
                 level_up=None, upgrade_skills=None, dialogue=None, debug_map=None, map_gen=None):
        self.owner = None
        self.main_menu = main_menu
        self.choose_animal = choose_animal
        self.choose_level = choose_level
        self.avatar_info = avatar_info
        self.level_up = level_up
        self.upgrade_skills = upgrade_skills
        self.dialogue = dialogue
        self.debug_map = debug_map
        self.map_gen = map_gen
        self.current_menu = None
        self.text_wrap = 60
        self.sel_index = 0
        self.viewport_w = 0
        self.viewport_h = 0
        self.padding_left = 10
        self.padding_right = 10
        self.padding_top = 15
        self.padding_bottom = 15

        if self.main_menu:
            self.main_menu.owner = self
        if self.choose_animal:
            self.choose_animal.owner = self
        if self.choose_level:
            self.choose_level.owner = self
        if self.avatar_info:
            self.avatar_info.owner = self
        if self.level_up:
            self.level_up.owner = self
        if self.upgrade_skills:
            self.upgrade_skills.owner = self
        if self.dialogue:
            self.dialogue.owner = self
        if self.debug_map:
            self.debug_map.owner = self
        if self.map_gen:
            self.map_gen.owner = self

    def show(self, menu):
        self.current_menu = menu
        self.owner.game_state = GameStates.MENU
        self.sel_index = 0
        self.viewport_w = self.owner.ui.viewport.offset_w
        self.viewport_h = self.owner.ui.viewport.offset_h
        output = MenuData(name=self.current_menu.name)
        message_list = MessageList()
        frame = FrameWithScrollbar(message_list)

        for item in menu.items:
            message_list.append(item)

        frame.update_geometry(
            self.padding_left + 1,
            self.padding_top,
            self.viewport_w + 5 - (self.padding_left + self.padding_right),
            self.viewport_h - (self.padding_top + self.padding_bottom))

        while output.menu_actions_left:

            # frame.draw()
            blt.layer(0)
            blt.color("white")
            self.owner.render_functions.clear_camera(5)
            # self.owner.render_functions.clear_menu(frame)
            current_line = 0
            line_index = 0
            # Draw heading
            blt.puts(self.padding_left, self.padding_top - 3, menu.heading.text_lines,
                     frame.width, align=blt.TK_ALIGN_CENTER)

            for item, height in message_list:
                item.color = "white"
                selected = line_index == self.sel_index
                blt.color("white")

                if current_line + height >= frame.offset:
                    # stop when message is below frame
                    if current_line - frame.offset > frame.height:
                        break
                    # drawing message
                    if selected:
                        blt.color("orange")
                        item.color = "orange"

                    text = "%s%s" % ("[U+203A] " if selected else " ", item.get_text())
                    blt.puts(self.padding_left, self.padding_top + current_line -
                             frame.offset + 5, text, frame.width, align=blt.TK_ALIGN_CENTER)

                current_line += height + 1
                line_index += 1

            #blt.crop(self.padding_left, self.padding_top, frame.width, frame.height)
            blt.refresh()

            sel = menu.items[self.sel_index].value if menu.items else None
            key = blt.read()

            output = self.handle_input(output, key, sel, menu.items, frame)
            if output.event == "break":
                if menu.title_screen:
                    exit()
                else:
                    self.owner.game_state = GameStates.PLAYER_TURN
                    self.owner.render_functions.clear_camera(5)
                    break
            elif output.params or output.sub_menu or not output.menu_actions_left:
                self.owner.render_functions.clear_camera(5)
                return output

    def handle_input(self, output, key, sel, items, frame):

        if key == blt.TK_CLOSE:
            exit()
        elif key == blt.TK_ESCAPE:
            output.event = "break"
            return output
        elif key == blt.TK_UP:
            if self.sel_index > 0:
                self.sel_index -= 1
            frame.scroll(-(frame.contents.heights[self.sel_index]))
        elif key == blt.TK_DOWN:
            if self.sel_index < len(items) - 1:
                self.sel_index += 1
            frame.scroll(frame.contents.heights[self.sel_index])
        elif key == blt.TK_RESIZED:
            frame.update_geometry(
                self.padding_left,
                self.padding_top,
                blt.state(blt.TK_WIDTH) - (self.padding_left + self.padding_right + 1),
                blt.state(blt.TK_HEIGHT) - (self.padding_top + self.padding_bottom))
        elif key == blt.TK_ENTER:
            if sel == "Resume game":
                output.event = "break"
                return output
            elif sel == "Exit":
                exit()
            elif sel == "New game":
                output.name = "choose_animal"
                output.sub_menu = True
                output.prev_menu = self.current_menu
            elif sel == "Map generator":
                output.name = "map_gen"
                output.sub_menu = True
                output.prev_menu = self.current_menu
            elif self.current_menu.name == "map_gen":
                output.params = sel
                output.event = "debug_map"
                output.prev_menu = self.current_menu
            elif self.current_menu.name == "choose_animal":
                output.params = sel
                output.event = "new_game"
            elif self.current_menu.name == "level_up":
                output.params = sel
                output.event = "level_up"
            elif self.current_menu.name == "upgrade_skills":
                output.params = sel
                output.event = "upgrade_skills"
                output = self.current_menu.spend_points(output)
            else:
                output.params = sel

        return output

    def handle_output(self, data):
        if data.sub_menu:
            self.create_or_show_menu(data)
            if self.current_menu.event == "show_prev_menu":
                data.prev_menu.show()
        elif data.event == "new_game":
            self.owner.init_new_game(params=data.params)
        elif data.event == "debug_map":
            debug_map_data = MenuData(name="debug_map", params=data.params, sub_menu=True, prev_menu=self.current_menu)
            self.owner.menus.create_or_show_menu(debug_map_data)
            self.owner.render_functions.clear_camera(5)
        elif self.current_menu.event == "level_change":
            self.owner.levels.biome = data.params
        self.owner.game_state = GameStates.PLAYER_TURN

    def create_or_show_menu(self, data):

        if data.name == "choose_animal":
            if self.choose_animal:
                self.choose_animal.refresh()
                self.choose_animal.show()
            else:
                choose_animal_menu = ChooseAnimal(sub_menu=data.sub_menu)
                self.choose_animal = choose_animal_menu
                self.choose_animal.owner = self
                self.choose_animal.show()
        elif data.name == "choose_level":
            if self.choose_level:
                self.choose_level.data = data.params
                self.choose_level.refresh()
                self.choose_level.show()
            else:
                choose_level_menu = ChooseLevel(data=data.params)
                self.choose_level = choose_level_menu
                self.choose_level.owner = self
                self.choose_level.show()
        elif data.name == "avatar_info":
            if self.avatar_info:
                self.avatar_info.data = data.params
                self.avatar_info.refresh()
                self.avatar_info.show()
            else:
                avatar_info_menu = AvatarInfo(data=data.params)
                self.avatar_info = avatar_info_menu
                self.avatar_info.owner = self
                self.avatar_info.show()
        elif data.name == "level_up":
            if self.level_up:
                self.level_up.data = data.params
                self.level_up.refresh()
            else:
                level_up_menu = LevelUp(data=data.params)
                self.level_up = level_up_menu
                self.level_up.owner = self
        elif data.name == "upgrade_skills":
            if self.upgrade_skills:
                self.upgrade_skills.data = data.params
                self.upgrade_skills.refresh()
            else:
                upgrade_skills_menu = UpgradeSkills(data=data.params)
                self.upgrade_skills = upgrade_skills_menu
                self.upgrade_skills.owner = self
        elif data.name == "dialogue":
            if self.dialogue:
                self.dialogue.show()
            else:
                dialogue_menu = DialogueMenu(data=data.params)
                self.dialogue = dialogue_menu
                self.dialogue.owner = self
        elif data.name == "map_gen":
            if self.map_gen:
                self.map_gen.data = data.params
                self.map_gen.refresh()
                self.map_gen.show()
            else:
                map_gen_menu = MapGen(sub_menu=data.sub_menu)
                self.map_gen = map_gen_menu
                self.map_gen.owner = self
                self.map_gen.show()
        elif data.name == "debug_map":
            if self.debug_map:
                self.debug_map.data = data.params
                self.debug_map.show(self.owner.render_functions.draw_debug_map)
            else:
                debug_map = DebugMap(data=data.params, sub_menu=data.sub_menu)
                self.debug_map = debug_map
                self.debug_map.owner = self
                self.debug_map.show(self.owner.render_functions.draw_debug_map)

        self.owner.game_state = GameStates.PLAYER_TURN


class MenuData:
    def __init__(self, name=None, sub_menu=False, prev_menu=None, params=None, event=None, menu_actions_left=True):
        self.name = name
        self.sub_menu = sub_menu
        self.prev_menu = prev_menu
        self.params = params
        self.event = event
        self.menu_actions_left = menu_actions_left
        self.messages = []
