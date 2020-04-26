

class MessageLog:

    def __init__(self, max_length):
        self.buffer = []
        self.history = []
        self.max_length = max_length
        self.new_msgs = False

    def send(self, msg):

        if isinstance(msg, list):
            for n in msg:
                self.history.append(n)
                if len(self.buffer) >= self.max_length:
                    self.buffer = self.buffer[:len(self.buffer) - 1]
                self.buffer.insert(0, n)
                self.new_msgs = True
        else:

            self.history.append(str(msg))
            if len(self.buffer) >= self.max_length:
                self.buffer = self.buffer[:len(self.buffer) - 1]

            self.buffer.insert(0, msg)
            self.new_msgs = True

    def clear(self):

        self.buffer = []
        self.new_msgs = True
