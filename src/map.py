from types import NoneType

class CharLenError(Exception):
    def __init__(self,len):
        super().__init__(f"Char cant be longer than 1 is {len}.")

class OutsideOfMapBoundsException(Exception):
    def __init__(self,x,y):
        super().__init__(f"Attempted to place object or Tile outside of the specified map: {x},{y}")

class ColorCodeError(Exception):
    def __init__(self,color_code):
        if color_code < 0:
            super().__init__(f"Color code is negative: {color_code}")
        elif color_code > 255:
            super().__init__(f"Color code is above 255: {color_code}")

class Color:
    def __init__(self,color_code:int):
        if color_code < -1 or color_code > 255:
            raise ColorCodeError(color_code)
        self.color_code = color_code

    def bg(self):
        if self.color_code == -1:
            return ""
        return f"\u001b[48;5;{self.color_code}m"

    def fg(self):
        if self.color_code == -1:
            return ""
        return f"\u001b[38;5;{self.color_code}m"

    def apply(self,text:str=" ",bg=False):
        if bg == True:
            return self.bg() + text + '\x1b[48;5;0m\x1b[38;5;15m'
        else:
            return self.fg() + text + '\x1b[48;5;0m\x1b[38;5;15m'

class Char:
    def __init__(self,text:str = "", fg: Color=Color(232), bg: Color=Color(-1)):
        if len(text) != 1:
            raise CharLenError(len(text))
        self.text = text
        self.fg = fg
        self.bg = bg

    def __repr__(self):
        return self.bg.apply(self.fg.apply(self.text,True)) + "\033[0m"

class Object:
    def __init__(self, char:Char,metadata:dict={}):
        self.char = char
        self.metadata = metadata

    def __repr__(self):
        return str(self.char)

    def update(self):
        pass

class Player(Object):
    def __init__(self,metadata:dict={}):
        self.char = Char("@")
        self.metadata = metadata

class TileOptions:
    def __init__(self,**kwargs):
        for k,v in kwargs:
            self.__setattr__(k,v)

class Tile:
    def __init__(self, char:Char,tileopts:TileOptions|None=None):
        self.char = char
        self.tileoptions = tileopts

    def __repr__(self):
        return str(self.char)

class Room:
    def __init__(self,x:int,y:int,base:Tile,name:str):
        self.tiles: list[list[Tile]] = [[base for _ in range(x)] for _ in range(y)]
        self.objects: list[list[Object | None]] = [[None for _ in range(x)] for _ in range(y)]
        self.name   = name
        self.exits  = []
        self.x: int = x
        self.y: int = y

    def add_object(self,x:int,y:int,z:Object):
        if x > self.x or y > self.y:
            raise OutsideOfMapBoundsException(x,y)

        self.objects[y][x] = z

    def set_tile(self,x:int,y:int,z:Tile):
        if x > self.x or y > self.y:
            raise OutsideOfMapBoundsException(x,y)

        self.tiles[y][x] = z

    def get_tile(self,x:int,y:int):
        if x > self.x or y > self.y:
            return None

        return self.tiles[y][x]

    def update(self):
        for y in self.objects:
            for x in y:
                if type(x) == Object:
                    x.update()

    def add_exit(self,x:int,y:int,room:str):
        self.exits.append({"x":x,"y":y,"room":room})

    def __repr__(self):
        tmp = ""
        for y,yt in enumerate(self.tiles):
            for x,tile in enumerate(yt):
                if type(self.objects[y][x]) != NoneType:
                    tmp += str(self.objects[y][x])
                else:
                    tmp += str(tile)
            tmp += "\n"
        return tmp

class Map:
    def __init__(self):
        self.rooms = {}
        self.current_room: None | str = None

    def add_room(self,room:Room):
        self.rooms[room.name] = room
        if self.current_room == None:
            self.current_room = room.name

    def get_current_room(self):
        return self.rooms[self.current_room]

    def __repr__(self):
        return str(self.rooms[self.current_room])

room = Room(10,10,Tile(Char("#")),"TestRoom")
room.add_object(5,5,Player())

map = Map()
map.add_room(room)
