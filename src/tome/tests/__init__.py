from tome.utils.logging import start
start(True)

from tome.client.client import Client
from socket import socket

class Test:
    def __init__(self, name:str="Test"):
        '''Initialize the test'''
        self.name = name

    def run(self) -> bool:
        '''Run the test and return the status, True: success False: Failure'''
        return True

def p(content):
    open("testlogs.txt",'a').write(content)

class TestingClient(Client):
    def __init__(self,bytesinbuffer=False):
        super().__init__(socket(),("",0),0,lambda: print("removed"))
        self.bytesinbuffer = bytesinbuffer
        self.buffer = []
        self.inputbuffer = []

    def send(self, content: str = "", lines=0,end="\n") -> None:
        self.buffer.append(("\n"*lines)+content+end)

    def bsend(self, content: bytes) -> None:
        if self.bytesinbuffer:
            self.buffer.append(content)

    def disconnect(self, message: str = "No disconnect message"):
        p(f"Tried to disconnect: {message}")

    def get(self) -> str:
        try:
            return self.inputbuffer.pop(0)
        except IndexError:
            p(f"No more inputs left from the inputbuffer")
            return ""

    def bget(self) -> bytes:
        try:
            popped = self.inputbuffer.pop(0)
            if type(popped) == str:
                return self.inputbuffer.pop(0).encode()
            elif type(popped) == bytes:
                return popped
            return b""

        except IndexError:
            p("No more inputs left from the inputbuffer")
            return b""

    def yn(self,question:str,preferred_option="y") -> bool:
        preferred_option = preferred_option.lower()
        if preferred_option != "n":
            self.send(question + "(Y/n): ")
        else:
            self.send(question + "(y/N): ")
        response = self.get()
        if preferred_option == "n":
            if response in ("yes","1","y"):
                return True
            else:
                return False
        else:
            if response in ("no","2","n"):
                return False
            else:
                return True

    def input(self, message:str="", echo:bool=True) -> str:
        try:
            return self.inputbuffer.pop(0)
        except IndexError:
            p(f"No more inputs left from the inputbuffer for: {message}")
            return ""

    def binput(self,message:str="") -> bytes:
        try:
            return self.inputbuffer.pop(0).encode()
        except IndexError:
            p("No more inputs left from the inputbuffer")
            return b""

    def tinput(self, message: str = "", typed: type = str) -> str | bool:
        if self.disconnected:
            return False
        try:
            return typed(self.input(message))
        except:
            if not self.disconnected:
                p(f"[{self.td}] Could not type input")
            return False

    def ltinput(self, message: str = "", typed: type = str, wrongmsg: str = "You needed to input a str."):
        while not self.disconnected:
            inp = self.tinput(message, typed)
            if inp is not False:
                return inp
            elif not self.disconnected:
                self.send(wrongmsg)
        return None
