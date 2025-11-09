from types import NoneType
class Object:
    def __init__(self, char:Char,metadata:dict=None):
        if metadata == None:
            metadata = {}
        self.char = char
        self.metadata = metadata

    def __repr__(self):
        return str(self.char)

    def update(self):
        pass

class Player(Object):
    def __init__(self,metadata:dict=None):
        if metadata == None:
            metadata = {}
        self.char = Char("@")
        self.metadata = metadata
from exceptions import CharLenError, OutsideOfMapBoundsException, RoomNotFoundError
from utils.color import Char

class TileOptions:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Tile:
    def __init__(self, char:Char,tileopts:TileOptions|None=None):
        self.char = char
        self.tileoptions = tileopts

    def __repr__(self):
        return str(self.char)

class Exit:
    def __init__(self,x:int,y:int,roomid:str):
        self.x = x
        self.y = y
        self.roomid = roomid

class Room:
    def __init__(self,x:int,y:int,base:Tile,name:str):
        self.tiles: list[list[Tile]] = [[base for _ in range(x)] for _ in range(y)]
        self.entities: list[Entity] = []
        self.name = name
        self.exits: list[Exit] = []
        self.x: int = x
        self.y: int = y

    def add_entity(self,entity:Entity):
        if entity.x > self.x or entity.y > self.y:
            raise OutsideOfMapBoundsException(entity.x,entity.y)

        self.entities.append(entity)

    def set_tile(self,x:int,y:int,z:Tile):
        if x >= self.x or y >= self.y:
            raise OutsideOfMapBoundsException(x, y)

        self.tiles[y][x] = z

    def get_tile(self,x:int,y:int):
        if x > self.x or y > self.y:
            return None

        return self.tiles[y][x]

    def update(self):
        for y in self.entities:
            for x in y:
                if type(x) == Entity:
                    x.update()

    def add_exit(self,exit_obj:Exit):
        self.exits.append(exit_obj)

    def __repr__(self):
        tmp = self.tiles
        for entity in self.entities:
            tmp[entity.y][entity.x] = str(entity)
        rep = ""
        for row in tmp:
            rep += "".join(row) + "\n"
        return rep

class Map:
    def __init__(self):
        self.rooms = {}

    def add_room(self,room:Room):
        self.rooms[room.name] = room
    
    def get_room(self,roomid:str):
        if roomid in self.room.keys():
            return self.rooms[roomid]
        else:
            raise RoomNotFoundError(roomid)
