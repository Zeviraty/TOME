from tome.exceptions import OutsideOfMapBoundsException, RoomNotFoundError
from tome.world.entities.entity import Entity 
from tome.utils.color import Char
import json

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
    
    def dump(self):
        return {"char": self.char.dump(),
                "opts": self.tileoptions.__dict__ if self.tileoptions != None else None
                }

class Exit:
    def __init__(self,x:int,y:int,roomid:str):
        self.x = x
        self.y = y
        self.roomid = roomid

    def dump(self):
        return self.__dict__

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

    def dump(self):
        tiles = []
        exits = [e.dump() for e in self.exits]
        last_tile = None
        run_count = 0
        for row in self.tiles:
            for tile in row:
                t = tile.dump()
                if last_tile is None:
                    last_tile = t
                    run_count = 1
                    continue
                if t == last_tile:
                    run_count += 1
                else:
                    lt = dict(last_tile)
                    lt["count"] = run_count
                    tiles.append(lt)
                    last_tile = t
                    run_count = 1
        if last_tile is not None:
            lt = dict(last_tile)
            lt["count"] = run_count
            tiles.append(lt)
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "tiles": tiles,
            "exits": exits,
        }

    @staticmethod
    def from_dump(dump:dict):
        r = Room(dump["x"],dump["y"],Char(" "),dump["name"])
        dump["tiles"]
        return r

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

    def dump(self):
        tmp = {}
        for k,v in self.rooms.items():
            tmp[k] = v.dump()
        return tmp

    @staticmethod
    def from_config(config_file:str):
        rmap = Map()
        d = json.load(open(f"config/maps/{config_file}.mf",'r'))
        for k,v in d.items():
            rmap.rooms[k] = Room.from_dump(v)
        return rmap
