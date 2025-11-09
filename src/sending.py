class Message:
    def __init__(self, receiver_id, sender_id, message):
        self.receiver_id = receiver_id
        self.sender_id = sender_id
        self.message = message

    def __repr__(self):
        return str(self.message)

class Sender:
    def __init__(self):
        self.messages = []

    def send(self, message, forced=False):
        if message in ([],{},"") and not forced:
            return
        self.messages.append(message)

    def receive(self, object_id):
        try:
            val = next(message for message in self.messages if message.receiver_id == object_id)
            self.messages.remove(val)
            return val
        except StopIteration:
            return None

global sender
sender = None

def init_sender():
    global sender
    sender = Sender()

def send(*args, **kwargs):
    global sender
    sender.send(*args,**kwargs)

def receive(*args, **kwargs):
    global sender
    return sender.receive(*args,**kwargs)

def receive_block(*args, **kwargs):
    global sender
    recv = sender.receive(*args,**kwargs)
    while recv == None:
        recv = sender.receive(*args,**kwargs)
    return recv
