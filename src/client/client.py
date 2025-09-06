import socket
import json
import threading
import hashlib
from utils.color import *
import db.utils as db
from utils.profanity import check_profanity
import utils.logging as log
import utils.config
import client.mainmenu as mm

TELNET_COMMANDS = {
    # Telnet command bytes (RFC 854)
    "IAC": bytes([255]),   # Interpret As Command
    "DONT": bytes([254]),
    "DO": bytes([253]),
    "WONT": bytes([252]),
    "WILL": bytes([251]),
    "SB": bytes([250]),    # Subnegotiation Begin
    "GA": bytes([249]),
    "EL": bytes([248]),
    "EC": bytes([247]),
    "AYT": bytes([246]),
    "AO": bytes([245]),
    "IP": bytes([244]),
    "BREAK": bytes([243]),
    "DM": bytes([242]),
    "NOP": bytes([241]),
    "SE": bytes([240]),    # Subnegotiation End

    # Telnet options (partial list, per IANA assignments)
    "BINARY": bytes([0]),
    "ECHO": bytes([1]),
    "SUPPRESS_GO_AHEAD": bytes([3]),
    "STATUS": bytes([5]),
    "TIMING_MARK": bytes([6]),
    "TERMINAL_TYPE": bytes([24]),
    "NAWS": bytes([31]),   # Negotiate About Window Size
    "TERMINAL_SPEED": bytes([32]),
    "REMOTE_FLOW_CONTROL": bytes([33]),
    "LINEMODE": bytes([34]),
    "ENVIRON": bytes([36]),

    # Common MUD extensions
    "GMCP": bytes([201]),  # Generic Mud Communication Protocol (community-defined)
}

INVERSE_TELNET = {v: k for k, v in TELNET_COMMANDS.items()}

class Client:
    def __init__(self, client: socket.socket, addr: tuple, id: int, remove_callback) -> None:
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
        self.character: dict = {}
        self.conn = db.get()
        self.remove_callback = remove_callback

    
    def menu(self,options:list[str],name="",input_string="Command: ",other_options: bool = False,string=False):
        menu = " " + YELLOW.apply(DARK_BLUE.apply(f'{name}:\n',bg=True))
        for idx,i in enumerate(options):
            menu += f" {DARK_BLUE.apply(YELLOW.apply(str(idx)), bg=True)}) {CYAN.apply(i)}\n"
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
            log.warn("broke pipe",self.td)
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
                self.gmcpsend("IAC WILL ECHO")
                self.getgmcp()

            self.send(message,end="")
            response = self.get().replace("\n","")

            if check_profanity(response):
                self.warn(f"Used banned word in message: {response}.")
            else:
                if echo == True and self.mudclient["client"] != "UNKNOWN":
                    if "client" in self.mudclient.keys() and self.mudclient['client'] == "Mudlet":
                        self.send(message+" "+DARK_YELLOW.apply(response).strip())
                    else:
                        self.send(DARK_YELLOW.apply(response).strip())

                
                if self.mudclient["client"] != "UNKNOWN":
                    self.gmcpsend("IAC WONT ECHO")
                    self.getgmcp()
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

    def getgmcp(self) -> dict:
        data = self.bget()
        gmcp_data = {}
        telnet_log = []

        i = 0
        while i < len(data):
            byte = data[i]

            if byte == TELNET_COMMANDS["IAC"][0]:
                i += 1
                if i >= len(data): break

                cmd = data[i]
                cmd_byte = bytes([cmd])
                cmd_name = INVERSE_TELNET.get(cmd_byte, f"UNKNOWN({cmd})")

                # Handle subnegotiation: IAC SB GMCP ... IAC SE
                if cmd == TELNET_COMMANDS["SB"][0] and i + 1 < len(data) and data[i + 1] == TELNET_COMMANDS["GMCP"][0]:
                    i += 2  # Skip SB and GMCP
                    start = i
                    while i < len(data) - 1:
                        if data[i] == TELNET_COMMANDS["IAC"][0] and data[i + 1] == TELNET_COMMANDS["SE"][0]:
                            payload = data[start:i].decode(errors="ignore")
                            if " " in payload:
                                key, value = payload.split(" ", 1)
                                try:
                                    gmcp_data[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    gmcp_data[key] = value
                            else:
                                gmcp_data[payload] = None
                            telnet_log.append(f"IAC SB GMCP {payload} IAC SE")
                            i += 2  # Skip IAC SE
                            break
                        i += 1
                    continue

                # Handle WILL/WONT GMCP
                elif cmd in [TELNET_COMMANDS["WILL"][0], TELNET_COMMANDS["WONT"][0], TELNET_COMMANDS["DO"][0], TELNET_COMMANDS["DONT"][0]] and i + 1 < len(data):
                    option = data[i + 1]
                    if option == TELNET_COMMANDS["GMCP"][0]:
                        gmcp_data["gmcp"] = (cmd == TELNET_COMMANDS["WILL"][0] or cmd == TELNET_COMMANDS["DO"][0])
                        telnet_log.append(f"IAC {cmd_name} GMCP")
                        i += 2
                        continue
                    else:
                        option_name = INVERSE_TELNET.get(bytes([option]), f"UNKNOWN({option})")
                        telnet_log.append(f"IAC {cmd_name} {option_name}")
                        i += 2
                        continue

                # Handle other commands with options (e.g., DO NAWS)
                elif i + 1 < len(data):
                    option = data[i + 1]
                    option_name = INVERSE_TELNET.get(bytes([option]), f"UNKNOWN({option})")
                    telnet_log.append(f"IAC {cmd_name} {option_name}")
                    i += 2
                    continue

                else:
                    telnet_log.append(f"IAC {cmd_name}")
                    i += 1

            else:
                telnet_log.append(str(byte))
                i += 1

        if telnet_log:
            gmcp_data["telnet"] = telnet_log

        return gmcp_data


    def bsend(self, content: bytes) -> None:
        try:
            self.client.send(content)
        except (BrokenPipeError, OSError):
            self.disconnect()

    def gmcpsend(self, content: str = "") -> None:
        message: bytes = b""
        for i in content.split(" "):
            if i in TELNET_COMMANDS.keys():
                message += TELNET_COMMANDS[i]
            else:
                message += i.encode()
        try:
            self.client.send(message)
        except (BrokenPipeError, OSError):
            self.disconnect()

    def send(self, content: str = "", lines=0,end="\n") -> None:
        try:
            sending = ("\n"*lines)+content+end
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
        log.disconnect(message,self.td)
        self.remove_callback(self)

    def warn(self,reason):
        self.disconnect(reason)
        log.warn("broke pipe",self.td)
        next_id = conn.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM warnings WHERE account_id = ?', (self.user[0],)).fetchone()[0]

        conn.execute('INSERT INTO warnings (id, account_id, reason) VALUES (?, ?, ?)', (next_id, self.user[0], reason))

        if next_id >= 3:
            conn.execute(f'UPDATE accounts SET banned = 1 WHERE id = {self.user[0]};')

        self.conn.commit()
        self.conn.close()
        exit(0)
