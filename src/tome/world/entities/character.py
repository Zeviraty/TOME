from .entity import Entity

class Character(Entity):
    def __init__(self,metadata:dict=None):
        if metadata == None:
            metadata = {}
        self.char = Char("@")
        self.metadata = metadata
