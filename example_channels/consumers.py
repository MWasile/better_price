from channels.generic.websocket import WebsocketConsumer


class SimpleConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data='XDDD')

    def receive(self, text_data=None, bytes_data=None):
        pass

    def disconnect(self, code):
        pass
