class OutsideOfMapBoundsException(Exception):
    def __init__(self, x, y):
        super().__init__(f"Coordinates ({x}, {y}) are outside of map bounds.")

class CharLenError(Exception):
    def __init__(self, length):
        super().__init__(f"Character length should be 1, got length {length}.")

class RoomNotFoundError(Exception):
    def __init__(self,roomid:str=""):
        super().__init__(f"Room: {roomid} not found")
