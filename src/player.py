import socket
import json
import threading
import db
import hashlib
from utils.color import *
from utils.profanity import check_profanity
import utils.logging as log

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

class Player:
    def __init__(self, client: socket.socket, addr: tuple, id: int) -> None:
        self.client: socket.socket = client
        self.addr: tuple = addr
        self.x: int = 0
        self.y: int = 0
        self.gmcp: bool = False
        self.mudclient: None | list = None
        self.id: int = id
        self.disconnected: bool = False
        self._disconnect_lock = threading.Lock()
        self.username: None | str = None
        self.user: tuple = ()
        self.td: int | str = id
        self.privileges: list = []
        self.character: dict = {}

    def mainmenu(self):
        while True:
            selected = self.menu(
                [
                    "New character",
                    "List characters",
                    "Exit",
                ],
                "Main Menu",
                "Command or Name of character: ",
                True,
            )
            conn = db.get()
            match selected:
                case 0:
                    self.send("New character\n")
                    menus = ["classes","races","name","gender","al1","al2","end"]
                    current_menu = 0

                    while True:
                        match menus[current_menu]:
                            case "classes":
                                classes = [
                                        "Paladin",
                                        "Fighter",
                                        "Rogue",
                                        "Mage",
                                        "Sorcerer",
                                        "Cleric",
                                        "Monk",
                                        "Warlock",
                                        "Barbarian",
                                        "Bard",
                                        "Druid",
                                        "Ranger",
                                    ]
                                classes.sort()
                                character_class = self.menu(
                                    classes,
                                    "Class",
                                )
                                character_class = classes[int(character_class)]
                                current_menu += 1
                            case "races":
                                races = {
                                    "Human": [],
                                    "Elf": ["Drow","High","Wood"],
                                    "Dwarf": ["Hill","Mountain"],
                                    "Dragonborn": [],
                                    "Gnome": ["Forest","Rock"],
                                    "Half-Elf": [],
                                    "Half-Orc": [],
                                    "Halfling": ["Lightfoot","Stout"],
                                    "Tiefling": [],
                                    "Back": [],
                                }

                                race: str = str(self.menu(
                                    list(raes.keys()),
                                    "\nRace",
                                    string=True
                                ))
                                if race == "Back":
                                    current_menu -= 1
                                else:
                                    if len(races[race]) > 0:
                                        sub_races = races[race]
                                        sub_races.append("Back")
                                        sub_race: str | None = str(self.menu(
                                            sub_races,
                                            "\nSub-Race",
                                            string=True
                                        ))
                                        if sub_race == "Back":
                                            del sub_race
                                        else:
                                            current_menu += 1
                                    else:
                                        sub_race: str | None = None
                                        current_menu += 1
                            case "name":
                                names = conn.execute("SELECT name FROM characters WHERE account_id = ?;",(self.user[0],)).fetchall()

                                while True:
                                    name = self.input("Character name: ")
                                    if (name,) in names:
                                        self.send("One of your characters already has that name.")
                                    else:
                                        break
                                current_menu += 1

                            case "gender":
                                gender = self.menu(
                                    [
                                        "Male",
                                        "Female",
                                        "Non-Binary",
                                        "Back"
                                    ],
                                    "\nGender",
                                    string=True
                                )
                                if gender == "Back":
                                    current_menu -=2
                                    del gender
                                else:
                                    current_menu += 1
                            case "al1":
                                al1 = self.menu(
                                    [
                                        "Lawful",
                                        "Neutral",
                                        "Chaotic",
                                        "Back"
                                    ],
                                    "\nFirst Alignment",
                                    string = True
                                )
                                if al1 == "Back":
                                    current_menu -= 1
                                    del al1
                                else:
                                    current_menu += 1
                            case "al2":
                                al2 = self.menu(
                                    [
                                        "Good",
                                        "Neutral",
                                        "Evil",
                                        "Back"
                                    ],
                                    "\nSecond Alignment",
                                    string = True
                                )
                                if al2 == "Back":
                                    current_menu -= 1
                                    del al2
                                else:
                                    current_menu += 1
                            case "end":
                                self.send("Is this correct?:\n")
                                self.send(f"Class    : {character_class}")
                                self.send(f"Race     : {race}{'-'+sub_race if sub_race != None else ''}")
                                self.send(f"Name     : {name}")
                                self.send(f"Gender   : {character_class}")
                                self.send(f"Alignment: {al1} {al2}")
                                if self.yn(""):
                                    break
                                else:
                                    current_menu -= 1
                    self.character["Class"] = character_class
                    self.character["Sub-race"] = sub_race
                    self.character["Race"] = race
                    self.character["Name"] = name
                    self.character["Gender"] = gender
                    self.character["A1"] = al1
                    self.character["A2"] = al2

                    conn.execute("INSERT INTO characters (name, account_id) VALUES (?,?)",(name,self.user[0]))
                    self.character["ID"] = conn.execute("SELECT id FROM characters WHERE account_id = ? AND name = ?;",(self.user[0],name,)).fetchone()[0]


                    for k,v in self.character.items():
                        if k == "Name" or k == "ID":
                            continue
                        conn.execute("INSERT INTO character_attributes (attr_name, attr_value, character_id) VALUES (?,?,?)",(k,v,self.character["ID"]))

                    conn.commit()
                    conn.close()
                    if self.yn("Play as "+name+"? "):
                        self.send()
                        break
                case 1:
                    self.send("")
                    characters = conn.execute("SELECT * FROM characters WHERE account_id = ?;",(self.user[0],))
                    self.send(YELLOW.fg()+Color(17).apply("Characters:                 ",bg=True)+DARK_BLUE.bg())
                    for character in characters:
                        self.send(f"{character[1]} {' ' * (22 - len(character[1]) - len(str(character[3])))}lvl: {character[3]}")
                    self.send(RESET)
                case 2:
                    self.disconnect("You chose to exit this realm.")
                    break
                case _:
                    characters = conn.execute("SELECT name, id FROM characters WHERE account_id = ?;",(self.user[0],)).fetchall()
                    if selected in [item[0] for item in characters]:
                        id = [item[1] if item[0] == selected else False for item in characters]
                        while False in id:
                            id.remove(False)
                        attributes = conn.execute("SELECT * FROM character_attributes WHERE character_id = ?;",(id[0],)).fetchall()
                    else:
                        self.send("Not the name of a character or a command.")

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

    def login(self, gmcp:bool = True) -> None:
        if gmcp:
            self.gmcpsend("IAC WILL GMCP")
            gmcp_response = self.getgmcp()
            if "gmcp" in gmcp_response.keys():
                self.gmcp = gmcp_response["gmcp"]
            if "Core.Hello" in gmcp_response.keys():
                self.mudclient = gmcp_response["Core.Hello"]

        username = self.input("Username:").lower()
        conn = db.get()
        passwords = conn.execute("SELECT password FROM accounts WHERE name = ?;",(username,)).fetchone()

        if passwords:
            password = self.input("Password: ",echo=False)

            if str(hashlib.sha256(password.encode()).digest()) == passwords[0]:
                self.send(f"Logged in as: {username}.\n")
                self.username = username
                self.user = conn.execute("SELECT * FROM accounts WHERE name = ?;",(username,)).fetchone()
                log.info(f"Logged in as: {self.username}",self.td)
                self.td = self.username
                privileges = conn.execute("SELECT privilege FROM account_privileges WHERE account_id = ?;",(self.user[0],)).fetchall()
                for i in privileges:
                    self.privileges.append(i[0])
            else:
                self.send("Wrong password.")
                self.login(False)

        else:
            create = self.yn("Account does not exist, do you want to create it? ",preferred_option="n")
            if create:
                while True:
                    password = self.input("Password: ",echo=False)
                    if password == self.input("Confirm password: ",echo=False):
                        break
                    else:
                        self.send("Passwords do not match.")

                conn.execute("INSERT INTO accounts (name, password) VALUES (?, ?)",
                    (
                        username,
                        str(hashlib.sha256(password.encode()).digest())
                    )
                )

                conn.commit()
                conn.close()

            self.login(False)

    def get(self) -> str:
        if self.disconnected:
            return ""
        try:
            return self.client.recv(2048).decode().strip()
        except (BrokenPipeError, OSError):
            self.disconnected = True
            return ""

    def bget(self) -> bytes:
        if self.disconnected:
            return b""
        try:
            return self.client.recv(2048)
        except (BrokenPipeError, OSError):
            self.disconnected = True
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
            exit(0)

    def input(self, message:str="", echo:bool=True) -> str:
        try:
            message = message.strip().replace("\n","")
            self.gmcpsend("IAC WILL ECHO")
            self.getgmcp()

            self.send(message,end="")
            response = self.get().replace("\n","")

            if check_profanity(response):
                self.disconnect(f"Used banned word in message: {response}.")
                log.warn("broke pipe",self.td)
                exit(0)
            else:
                if echo == True:
                    self.send(DARK_YELLOW.apply(response).strip())

                self.gmcpsend("IAC WONT ECHO")
                self.getgmcp()
                return response
        except BrokenPipeError:
            log.disconnect("broke pipe",self.td)
            exit(0)

    def binput(self,message:str="") -> bytes:
        try:
            self.send(message)
            return self.bget()
        except BrokenPipeError:
            log.disconnect("broke pipe",self.td)
            exit(0)

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
        except BrokenPipeError:
            log.disconnect("broke pipe",self.td)
            exit(0)

    def gmcpsend(self, content: str = "") -> None:
        message: bytes = b""
        for i in content.split(" "):
            if i in TELNET_COMMANDS.keys():
                message += TELNET_COMMANDS[i]
            else:
                message += i.encode()
        try:
            self.client.send(message)
        except BrokenPipeError:
            log.disconnect("broke pipe",self.td)
            exit(0)

    def send(self, content: str = "", lines=0,end="\n") -> None:
        try:
            sending = ("\n"*lines)+content+end
            self.client.send(sending.encode())
        except BrokenPipeError:
            log.disconnect("broke pipe",self.td)
            exit(0)

    def disconnect(self, message: str = "Disconnected.") -> None:
        with self._disconnect_lock:
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
