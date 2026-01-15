from utils.color import Char

class Entity:
    def __init__(self,x:int,y:int, char:Char,metadata:dict=None):
        if metadata == None:
            metadata = {}
        self.char = char
        self.metadata = metadata
        self.x = x
        self.y = y

    def __repr__(self):
        return str(self.char)

    def update(self):
        pass

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
