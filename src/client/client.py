import socket
import threading
from utils.color import *
import db.utils as db
from utils.profanity import check_profanity
import utils.logging as log
import utils.config
import client.mainmenu as mm
import sending
import client.telnet as telnet
from world.entities.character import Character

class Client:
    def __init__(self, client: socket.socket, addr: tuple, id: int, remove_callback, debug=False, showtelnet=False) -> None:
        self.client: socket.socket = client
        self.addr: tuple = addr
        self.x: int = 0
        self.y: int = 0
        self.gmcp: bool = False
        self.mudclient: None | list = None
        self.id: int = id
        self.disconnected: bool = False
        self.username: None | str = None
        self.user: tuple = ()
        self.td: int | str = id
        self.privileges: list = []
        self.character: Character | None = None
        self.conn = db.get()
        self.remove_callback = remove_callback
        self.debug: bool = debug
        self.showtelnet: bool = showtelnet
    
    def menu(self,options:list[str],name="",input_string="Command: ",other_options: bool = False,string=False):
        menu = " " + YELLOW.apply(DARK_BLUE.apply(f'{name}:\n',bg=True))
        for idx,i in enumerate(options):
            menu += f" {DARK_BLUE.apply(reset=False, bg=True)}{YELLOW.apply(str(idx))}) {CYAN.apply(i)}\n"
        self.send(menu)
        while True:
            recv = self.input(input_string)
            try:
                recv = int(recv)
            except:
                pass
            if recv in options or (type(recv) == int and recv in range(len(options))):
                if string:
                    if type(recv) == str:
                        return recv
                    else:
                        return options[int(recv)]
                else:
                    if type(recv) == int:
                        return recv
                    else:
                        return options.index(str(recv))
            elif other_options == True:
                return recv

    def pmenu(self,pages:list[dict]):
        current_menu = 0
        chosen = {}
        while current_menu < len(pages):
            page = pages[current_menu]
            if page["type"] == "options":
                options = page["options"]
                if current_menu != 0:
                    options.append("Back")
                recv = self.menu(
                    page["options"],
                    page["name"],
                    string=True
                )
                if recv == "Back":
                    current_menu -= 1
                else:
                    chosen[page["name"]] = recv
                    current_menu += 1
            elif page["type"] == "custom":
                recv = page["function"](self)
                if recv == "Back":
                    current_menu -= 1
                else:
                    chosen = {**recv,**chosen}
                    current_menu += 1
            elif page["type"] == str:
                recv = self.input(f"Input: {page['name']}{' (or back)' if current_menu != 0 else ''}: ")
                if recv.lower() == "back" and current_menu != 0:
                    current_menu -= 1
                else:
                    chosen[page["name"]] = recv
                    current_menu += 1
            else:
                pass
        return chosen


    def get(self) -> str:
        if self.disconnected:
            return ""
        try:
            return self.client.recv(2048).decode().strip()
        except (BrokenPipeError, OSError):
            self.disconnect()
            return ""
        except UnicodeDecodeError:
            return ""

    def bget(self) -> bytes:
        if self.disconnected:
            return b""
        try:
            return self.client.recv(2048)
        except (BrokenPipeError, OSError):
            self.disconnect()
            return b""
        except UnicodeDecodeError:
            return b""

    def yn(self,question:str,preferred_option="y") -> bool:
        try:
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
        except BrokenPipeError:
            log.warn("broke pipe",name=str(self.td))
            self.conn.close()
            self.disconnect()
            exit(0)
        except OSError:
            self.disconnect()
            exit(0)

    def input(self, message:str="", echo:bool=True) -> str:
        try:
            message = message.strip().replace("\n","")
            if self.mudclient["client"] != "UNKNOWN":
                telnet.send(self, "IAC WILL ECHO")
                telnet.get(self)

            self.send(message,end="")
            response = self.get().replace("\n","")
            if response == "map":
                sending.send(sending.Message("World",self.td,{}))

            if check_profanity(response):
                self.warn(f"Used banned word in message: {response}.")
            else:
                if echo == True and self.mudclient["client"] != "UNKNOWN":
                    if "client" in self.mudclient.keys() and self.mudclient['client'] == "Mudlet":
                        if message != "":
                            self.send(message+" "+DARK_YELLOW.apply(response).strip())
                        else:
                            self.send(DARK_YELLOW.apply(response))
                    else:
                        self.send(DARK_YELLOW.apply(response).strip())

                
                if self.mudclient["client"] != "UNKNOWN":
                    telnet.send(self, "IAC WONT ECHO")
                    telnet.get(self)
                return response
        except (BrokenPipeError, OSError):
            self.disconnect()

    def binput(self,message:str="") -> bytes:
        try:
            self.send(message)
            return self.bget()
        except (BrokenPipeError, OSError):
            self.disconnect()

    def tinput(self, message: str = "", typed: type = str) -> str | bool:
        if self.disconnected:
            return False
        try:
            return typed(self.input(message))
        except:
            if not self.disconnected:
                print(f"[{self.td}] Could not type input")
            return False

    def ltinput(self, message: str = "", typed: type = str, wrongmsg: str = "You needed to input a str."):
        while not self.disconnected:
            inp = self.tinput(message, typed)
            if inp is not False:
                return inp
            elif not self.disconnected:
                self.send(wrongmsg)
        return None

    def bsend(self, content: bytes) -> None:
        try:
            self.client.send(content)
        except (BrokenPipeError, OSError):
            self.disconnect()

    def send(self, content: str = "", lines=0,end="\n") -> None:
        try:
            sending = ("\n"*lines)+str(content)+end
            self.client.send(sending.encode())
        except (BrokenPipeError, OSError):
            self.disconnect()

    def sendtable(self, title: str, items: dict, compact: bool = False) -> None:
        keys = list(items.keys())
        num_rows = len(items[keys[0]]) if keys else 0

        self.send(YELLOW.fg() + Color(17).apply(f"{title:<25}", bg=True) + DARK_BLUE.bg())

        if compact:
            for i in range(num_rows):
                line = " ".join(f"{key}: {items[key][i]}" for key in keys)
                self.send(line)
            col_widths = {key: max(len(key), max(len(str(val)) for val in items[key])) for key in keys}
            header = "  ".join(f"{key:<{col_widths[key]}}" for key in keys)
            self.send(header)

            for i in range(num_rows):
                row = "  ".join(f"{str(items[key][i]):<{col_widths[key]}}" for key in keys)
                self.send(row)

    def disconnect(self, message: str = "Disconnected.") -> None:
        if self.disconnected:
            return
        self.disconnected = True
        try:
            self.send(f"Disconnected: {message}")
        except:
            pass
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.client.close()
        except:
            pass
        log.disconnect(message,name=str(self.td))
        self.remove_callback(self)

    def warn(self,reason):
        self.disconnect(reason)
        log.warn("broke pipe",name=str(self.td))
        next_id = self.conn.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM warnings WHERE account_id = ?', (self.user[0],)).fetchone()[0]

        self.conn.execute('INSERT INTO warnings (id, account_id, reason) VALUES (?, ?, ?)', (next_id, self.user[0], reason))

        if next_id >= 3:
            self.conn.execute(f'UPDATE accounts SET banned = 1 WHERE id = {self.user[0]};')

        self.conn.commit()
        self.conn.close()
        exit(0)
