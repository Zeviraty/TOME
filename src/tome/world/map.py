from tome.exceptions import OutsideOfMapBoundsException, RoomNotFoundError
from .entities.entity import Entity 
from tome.utils.color import Char
import json

class TileOptions:
    '''
    Extra tile data
    '''
    def __init__(self, **kwargs):
        '''
        Initializes a TileOptions class
        '''
        for k, v in kwargs.items():
            setattr(self, k, v)

class Tile:
    '''
    Class representing a singular Tile
    '''
    def __init__(self, char:Char,tileopts:TileOptions|None=None):
        '''
        Initializes a Tile class

        Parameters
        ----------
        char : Char
            Character for the tile
        tileopts : TileOptions|None, optional
            Options for the tile (default is None)
        '''
        self.char = char
        self.tileoptions = tileopts

    def __repr__(self):
        '''
        Get char as a string
        '''
        return str(self.char)
    
    def dump(self):
        '''
        Get tile as a dict
        '''
        return {"char": self.char.dump(),
                "opts": self.tileoptions.__dict__ if self.tileoptions != None else None
                }

class Exit:
    '''
    Exit to another room
    '''
    def __init__(self,x:int,y:int,roomid:str):
        '''
        Initializes an Exit class

        Parameters
        ----------
        x : int
            Horizontal position of exit
        y : int
            Vertical position of exit
        roomid : str
            Room to exit to
        '''
        self.x = x
        self.y = y
        self.roomid = roomid

    def dump(self):
        '''
        Returns Exit as a dict
        '''
        return self.__dict__

class Room:
    '''
    Class representing a room
    '''
    def __init__(self,x:int,y:int,base:Tile,name:str):
        '''
        Initialize a room object

        Parameters
        ----------
        x : int
            Horizontal size of room
        y : int
            Vertical size of room
        base : Tile
            Base tile
        name : str
            Name of room
        '''
        self.tiles: list[list[Tile]] = [[base for _ in range(x)] for _ in range(y)]
        self.entities: list[Entity] = []
        self.name = name
        self.exits: list[Exit] = []
        self.x: int = x
        self.y: int = y

    def add_entity(self,entity:Entity):
        '''
        Add an entity to a room

        Parameters
        ----------
        entity : Entity
            Entity to add

        Raises
        ------
        OutsideOfMapBoundsException:
            Raised if the entity is outside of the room
        '''
        if entity.x > self.x or entity.y > self.y:
            raise OutsideOfMapBoundsException(entity.x,entity.y)

        self.entities.append(entity)

    def set_tile(self,x:int,y:int,z:Tile):
        '''
        Set a tile in the room

        Parameters
        ----------
        x : int
            Horizontal position in the room
        y : int
            Vertical position in the room
        z : Tile
            Tile to set

        Raises
        ------
        OutsideOfMapBoundsException:
            Raised if tile is placed outside of room bounds
        '''
        if x >= self.x or y >= self.y:
            raise OutsideOfMapBoundsException(x, y)

        self.tiles[y][x] = z

    def get_tile(self,x:int,y:int):
        '''
        Get tile at position

        Parameters
        ----------
        x : int
            Horizontal position of tile
        y : int
            Vertical position of tile
        '''
        if x > self.x or y > self.y:
            return None

        return self.tiles[y][x]

    def update(self):
        '''
        Update all entities in the room
        '''
        for y in self.entities:
            for x in y:
                if type(x) == Entity:
                    x.update()

    def add_exit(self,exit_obj:Exit):
        '''
        Add an exit to the room

        Parameters
        ----------
        exit_obj : Exit
            Exit to add
        '''
        self.exits.append(exit_obj)

    def __repr__(self):
        '''
        Get room as string
        '''
        tmp = self.tiles
        for entity in self.entities:
            tmp[entity.y][entity.x] = str(entity)
        rep = ""
        for row in tmp:
            rep += "".join(row) + "\n"
        return rep

    def dump(self):
        '''
        Get room as a dict
        '''
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
        '''
        Initialize a room from a dict dump

        Parameters
        ----------
        dump : dict
            Dump to use
        '''
        r = Room(dump["x"],dump["y"],Char(" "),dump["name"])
        dump["tiles"]
        return r

class Map:
    '''
    A class representing an entire map
    '''
    def __init__(self):
        '''
        Initialize a map object
        '''
        self.rooms = {}

    def add_room(self,room:Room):
        '''
        Add a room to the map

        Parameters
        ----------
        room : Room
            Room to add
        '''
        self.rooms[room.name] = room
    
    def get_room(self,roomid:str):
        '''
        Get a room in the map

        Parameters
        ----------
        roomid : str
            Id of the room

        Raises
        ------
        RoomNotFoundError:
            Raised if the room is not found
        '''
        if roomid in self.room.keys():
            return self.rooms[roomid]
        else:
            raise RoomNotFoundError(roomid)

    def dump(self):
        '''
        Dump a map to a dict
        '''
        tmp = {}
        for k,v in self.rooms.items():
            tmp[k] = v.dump()
        return tmp

    @staticmethod
    def from_config(config_file:str):
        '''
        Load a map from config

        Parameters
        ----------
        config_file : str
            Path to config
        '''
        rmap = Map()
        d = json.load(open(f"config/maps/{config_file}.mf",'r'))
        for k,v in d.items():
            rmap.rooms[k] = Room.from_dump(v)
        return rmap
