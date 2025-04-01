import socket, requests
import sqlite3

IAC  = bytes([255])
SB   = bytes([250])
GMCP = bytes([201])
SE   = bytes([240])
WILL = bytes([251])

class Player:
    def __init__(self, client: socket.socket, addr:tuple):
        self.client = client
        self.addr = addr
        self.x =
        self.y =

    def bsend(self,content: bytes):
        try:
            self.client.send(content)
        except BrokenPipeError:
            print("[+] broke pipe")
            exit(0)

    def gmcpsend(self,content=""):
        try:
            self.client.send(IAC + SB + GMCP + content.encode() + IAC + SE, socket.MSG_OOB)
        except BrokenPipeError:
            print("[+] broke pipe")
            exit(0)

    def send(self,content="",lines=0):
        try:
            sending = ("\n"*lines)+content+"\n"
            self.client.send(sending.encode())
        except BrokenPipeError:
            print("[+] broke pipe")
            exit(0)



