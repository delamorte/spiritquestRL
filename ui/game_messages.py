

class MessageLog:

    def __init__(self, max_length):
        self.buffer = []
        self.buffer_colors = []
        self.history = []
        self.history_colors = []
        self.max_length = max_length
        self.new_msgs = False

    def send(self, msg):

        if isinstance(msg, list):
            for n in msg:
                if isinstance(n, str):
                    n = [n, "white"]
                elif len(n) == 1:
                    n = [n[0], "white"]
                self.history.append(n[0])
                self.history_colors.append(n[1])
                if len(self.buffer) >= self.max_length:
                    self.buffer = self.buffer[:len(self.buffer) - 1]
                if len(self.buffer_colors) >= self.max_length:
                    self.buffer_colors = self.buffer_colors[:len(self.buffer_colors) - 1]
                self.buffer.insert(0, n[0])
                self.buffer_colors.insert(0, n[1])
                self.new_msgs = True
        else:
            if isinstance(msg, str):
                msg = [msg, "white"]
            self.history.append(str(msg[0]))
            self.history_colors.append(msg[1])
            if len(self.buffer) >= self.max_length:
                self.buffer = self.buffer[:len(self.buffer) - 1]
            if len(self.buffer_colors) >= self.max_length:
                self.buffer_colors = self.buffer_colors[:len(self.buffer_colors) - 1]
            self.buffer.insert(0, msg[0])
            self.buffer_colors.insert(0, msg[1])
            self.new_msgs = True

    def clear(self):

        self.buffer = []
        self.new_msgs = True
