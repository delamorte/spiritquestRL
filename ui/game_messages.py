class MessageLog:

    def __init__(self, max_length):
        self.buffer = []
        self.history = []
        self.max_length = max_length

    def send(self, msg):

        self.history.append(str(msg))
        if len(self.buffer) >= self.max_length:
            self.buffer = self.buffer[:len(self.buffer) - 1]

        self.buffer.insert(0, msg)

    def update(self, buffer):
        buffer_state = buffer
        if len(self.buffer) != len(buffer_state):
            return True

    def clear(self):

        self.buffer = []
