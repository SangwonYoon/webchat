class Message():
    def __init__(self, message_type, content):
        self.message_type = message_type
        self.content = content

    def get_json(self):
        json = {"message_type": self.message_type, "content": self.content}
        return json