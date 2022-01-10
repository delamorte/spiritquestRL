

class MessageLog:

    def __init__(self, max_length):
        self.owner = None
        self.buffer = []
        self.history = []
        self.max_length = max_length
        self.new_msgs = False

    def send(self, messages):

        if not isinstance(messages, list):
            messages = [messages]

        for message in messages:
            if self.buffer and self.buffer[0].msg == message.msg:
                self.buffer[0].stacked += 1
                self.new_msgs = True
                continue
            if message.clear_buffer:
                self.clear()
            if message.extend_line:
                msg = self.buffer[0].msg + " {0}".format(message.msg)
                self.buffer[0].msg = msg
                self.history[-1].msg = msg
            else:
                self.history.append(message)
                if len(self.buffer) >= self.max_length:
                    self.buffer = self.buffer[:len(self.buffer) - 1]
                self.buffer.insert(0, message)
                self.new_msgs = True

    def clear(self):

        self.buffer = []
        self.new_msgs = True
