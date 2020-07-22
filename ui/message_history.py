from draw import clear_camera
from bearlibterminal import terminal as blt
from math import ceil
import variables

padding_left = 10
padding_right = 10
padding_top = 5
padding_bottom = 15


class MessageList(object):
    def __init__(self):
        self.total_height = 1
        self.texts = []
        self.heights = []

    def update_heights(self, width):
        self.heights = [blt.measure(text, width)[1] for text in self.texts]
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
        blt.bkcolor("none")
        blt.color("dark orange")
        self.scrollbar_column = self.left + self.width
        self.scrollbar_offset = int(
            (self.top + (self.height - self.scrollbar_height) * (
                self.offset / (self.contents.total_height - self.height))) *
            blt.state(blt.TK_CELL_HEIGHT))
        for i in range(self.scrollbar_height):
            blt.put_ext(self.scrollbar_column, i, 0,
                        self.scrollbar_offset, 0x2588)


def show_msg_history(message_log, name):
    messages = MessageList()
    frame = FrameWithScrollbar(messages)

    for msg in message_log:
        messages.append(msg)

    # Initial update
    frame.update_geometry(
        padding_left+1,
        padding_top,
        variables.viewport_w +5- (padding_left + padding_right),
        variables.viewport_h - (padding_top + padding_bottom))

    if name == "Message history":
        prompt = \
            "Message history: \n"

    elif name == "Inventory":
        prompt = \
            "Inventory: \n"

    while True:

        frame.draw()
        blt.color("white")

        blt.layer(0)
        clear_camera(5)
        current_line = 0
        blt.puts(padding_left, padding_top - frame.offset, prompt, frame.width)
        for text, height in messages:
            if current_line + height >= frame.offset:
                # stop when message is below frame
                if current_line - frame.offset > frame.height:
                    break
                # drawing message
                blt.puts(padding_left, padding_top + current_line -
                         frame.offset + 5, text, frame.width)
            current_line += height + 1

        blt.crop(padding_left, padding_top, frame.width, frame.height)

        # Render
        blt.refresh()

        key = blt.read()

        if key in (blt.TK_CLOSE, blt.TK_ESCAPE, blt.TK_M):
            blt.clear()
            break

        elif key == blt.TK_I and name is "Inventory":
            blt.clear()
            break

        elif key == blt.TK_UP:
            frame.scroll(-1)

        elif key == blt.TK_DOWN:
            frame.scroll(1)

        elif key == blt.TK_RESIZED:
            frame.update_geometry(
                padding_left,
                padding_top,
                blt.state(blt.TK_WIDTH) - (padding_left + padding_right + 1),
                blt.state(blt.TK_HEIGHT) - (padding_top + padding_bottom))
