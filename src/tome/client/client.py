import socket
from tome.utils.color import *
import tome.db.utils as db
from tome.utils.profanity import check_profanity
import tome.utils.logging as log
import tome.sending as sending
from . import telnet as telnet
from tome.world.entities.character import Character
import sqlite3
import typing
import collections.abc as abc
from typing import Any

class Client:
    '''
    Class representing a single connection to the server.

    Attributes
    ----------
    x : int
        X location of character (TODO: move to Character)
    y : int
        Y location of character (TODO: move to Character)
    gmcp : bool
        Whether the connection supports GMCP (Generic MUD Communication Protocol).
    mudclient : dict | None
        Data of MUD client used by the connection (set by mainmenu).
    disconnected : bool
        Whether the client has disconnected.
    username : str | None
        Username of the user.
    user : tuple
        Raw user data from the database.
    privileges : list[str]
        List of privileges the user has.
    character : Character | None
        The character the user is controlling.
    character_data : dict[str, Any]
        Data of the character
    conn : sqlite3.Connection
        Database connection.
    client : socket.socket
        Client socket.
    addr : tuple[str, int]
        Address of the connected client.
    id : int
        ID of the client.
    td : int | str
        Name used in logs for the client.
    remove_callback : typing.Callable
        Callback used to remove the client after disconnect.
    debug : bool
        Whether debug logging is enabled.
    showtelnet : bool
        Whether all telnet commands are shown.
    '''

    x: int = 0
    y: int = 0

    gmcp: bool = False
    mudclient: dict | None = None
    disconnected: bool = False

    username: str | None = None
    user: tuple
    privileges: list[str]
    character: Character | None = None
    character_data: dict[str, Any]

    conn: sqlite3.Connection
    client: socket.socket
    addr: tuple[str, int]
    id: int
    td: int | str
    remove_callback: typing.Callable
    debug: bool
    showtelnet: bool

    def __init__(self, client: socket.socket, addr: tuple[str, int], id: int, remove_callback: typing.Callable, debug: bool = False, showtelnet: bool = False) -> None:
        '''
        Initializes a Client object

        Parameters
        ----------
        client : socket.socket
            Client socket.
        addr : tuple[str, int]
            Address of the connected client.
        id : int
            ID of the client.
        remove_callback : typing.Callable
            Callback used to remove the client after disconnect.
        debug : bool, optional
            Whether debug logging is enabled. (default is False)
        showtelnet : bool, optional
            Whether all telnet commands are shown. (default is False)
        '''
        self.client = client
        self.addr = addr
        self.id = id
        self.td = id
        self.remove_callback = remove_callback
        self.debug = debug
        self.showtelnet = showtelnet
        self.character_data = {}

        self.privileges = []
        self.user = ()
        self.conn = db.get()
    
    def menu(self, options:list[str], name: str = "", input_string: str ="Command: ", other_options: bool = False, string: bool = False):
        '''
        Displays selection menu to the Client

        Parameters
        ----------
        options : list[str]
            Selectable options in menu
        name : str, optional
            Name of menu (default is "")
        input_string: str, optional
            String shown at bottom (default is "Command: ")
        other_options: bool, optional
            Whether the Client can input other options than in the list (default is False)
        string: bool, optional
            Whether the return type should be a string or the index (default is False)
        '''
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

    def pmenu(self, pages:list[dict[str, typing.Any]]) -> dict[str, typing.Any]:
        '''
        Shows a multi-page menu to the client.

        Each page dictionary must contain at least:
            - "type": Type of the page.
            - "name": Name of menu & Key to retrieve data from.

        Supported page types:
            - "options":
                Expects an "options" list. Displays a selectable menu using
                `self.menu(...)`. A "Back" option is automatically added if this
                is not the first page.
                The selected option is stored under the page's name.

            - "custom":
                Expects a callable under "function". The function is called with
                `self` and should return either:
                    - "Back" to navigate to the previous page
                    - A dict of values to merge into the chosen results.

            - str:
                Normal input using `self.input(...)`.
                Typing "back" (case-insensitive) navigates to the previous page
                when not on the first page.

        Parameters
        ----------
        pages : list[dict[str, Any]]
            A list of page definitions

        Returns
        -------
        dict[str, Any]
            All the selected options indexed by menu name

        Raises
        ------
        ValueError
            if keys are missing, or the wrong type
        '''
        current_menu = 0
        chosen = {}
        while current_menu < len(pages):
            page = pages[current_menu]
            if "type" not in page or "name" not in page:
                raise ValueError("Page should have 'name' & 'type' keys")
            if str not in (type(page['name']), type(page['type'])):
                raise ValueError("'name' and 'type' keys should be strings")
            if page["type"] == "options":
                if "options" not in page:
                    raise ValueError("Page with type 'options' should have a 'options' key")
                if type(page["options"]) != list:
                    raise ValueError("'options' key should be a list")
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
                if "function" not in page:
                    raise ValueError("Page with type 'custom' should have a 'function' key")
                if not page['function'] is typing.Callable:
                    raise ValueError("'function' key should be Callable")
                recv = page["function"](self)
                if recv == "Back":
                    current_menu -= 1
                else:
                    chosen = {**recv,**chosen}
                    current_menu += 1
            elif page["type"] == 'str':
                recv = self.input(f"Input: {page['name']}{' (or back)' if current_menu != 0 else ''}: ")
                if recv.lower() == "back" and current_menu != 0:
                    current_menu -= 1
                else:
                    chosen[page["name"]] = recv
                    current_menu += 1
            else:
                raise ValueError("Page type needs to be: 'options', 'custom' or 'str'")
        return chosen


    def get(self) -> str:
        '''
        Gets basic input from the Client (blocking)

        Returns
        -------
        str
            Input of the Client
        '''
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
        '''
        Gets basic input from the Client as raw bytes (blocking)

        Returns
        -------
        bytes
            Input of the Client
        '''
        if self.disconnected:
            return b""
        try:
            return self.client.recv(2048)
        except (BrokenPipeError, OSError):
            self.disconnect()
            return b""
        except UnicodeDecodeError:
            return b""

    def yn(self,question:str,preferred_option: str ="y") -> bool:
        '''
        Displays a yes/no question to the Client

        Parameters
        ----------
        question : str
            Question displayed to the client
        preferred_option : {'y', 'n'}, optional
            Needs to be either 'y' or 'n'
            standard selected option when Client sends an empty message

        Returns
        -------
        bool
            True if answer is 'y'
            False if answer is 'n'

        Raises
        ------
        ValueError
            if preferred_option is not 'y' or 'n'
        '''
        if preferred_option.lower() not in ('y','n'):
            raise ValueError("'preferred_option' needs to be in ('y', 'n')")
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
        '''
        Gets input from client (similar to default python `input()` function)

        Parameters
        ----------
        message : str, optional
            Message to display (default is '')
        echo : bool, optional
            Whether the answer should be echoed back or not

        Returns
        -------
        str
            Input of Client
        '''
        if self.mudclient == None:
            raise ValueError("Input called before client auth")
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
            return ""

    def binput(self,message:str="") -> bytes:
        '''
        Send message & get byte input from Client

        Parameters
        ----------
        message : str, optional
            Message to send (default is '')

        Returns
        -------
        bytes
            Client input
        '''
        try:
            self.send(message)
            return self.bget()
        except (BrokenPipeError, OSError):
            self.disconnect()
            return b''

    def bsend(self, content: bytes) -> None:
        '''
        Send bytes to Client

        Parameters
        ----------
        content : bytes
            Bytes to send
        '''
        try:
            self.client.send(content)
        except (BrokenPipeError, OSError):
            self.disconnect()

    def send(self, content: str = "", lines: int = 0,end: str = "\n") -> None:
        '''
        Send string to Client

        Parameters
        ----------
        content : str, optional
            String to send (default is '')
        lines : int, optional
            Amount of lines to prepend before content (default is 0)
        end : str, optional
            String to append to content (default is '\\n')
        '''
        try:
            sending = ("\n"*lines)+str(content)+end
            self.client.send(sending.encode())
        except (BrokenPipeError, OSError):
            self.disconnect()

    def sendtable(self, title: str, items: dict[str,abc.Sequence]) -> None:
        '''
        Send formatted table to Client

        Parameters
        ----------
        title : str
            Title of the table
        items : dict[str,collections.abc.Sequence]
            Items of table, formatted as:
            {'COLUMNNAME': ['ROW1','ROW2']}

        Raises
        ------
        ValueError
            Raised when not all columns have the same number of rows
        '''
        if not items:
            self.send("(no data)")
            return

        keys = list(items.keys())
        lengths = {key: len(items[key]) for key in keys}

        if len(set(lengths.values())) != 1:
            raise ValueError("All columns must have the same number of rows")

        num_rows = next(iter(lengths.values()))

        self.send(
            YELLOW.fg()
            + Color(17).apply(f"{title:<25}", bg=True)
            + DARK_BLUE.bg()
        )

        for i in range(num_rows):
            self.send(" ".join(f"{key}: {items[key][i]}" for key in keys))

        col_widths = {
            key: max(
                len(key),
                max(len(str(value)) for value in items[key])
            )
            for key in keys
        }

        header = "  ".join(
            f"{key:<{col_widths[key]}}" for key in keys
        )
        self.send(header)

        for i in range(num_rows):
            row = "  ".join(
                f"{str(items[key][i]):<{col_widths[key]}}"
                for key in keys
            )
            self.send(row)

    def disconnect(self, message: str = "Disconnected.") -> None:
        '''
        Disconnect Client

        Parameters
        ----------
        message : str, optional
            Reason for disconnect (default is 'Disconnected.')
        '''
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

    def warn(self,reason: str):
        '''
        Give user a waring

        Parameters
        ----------
        reason : str
            Reason for warning
        '''
        self.disconnect(reason)
        log.warn("broke pipe",name=str(self.td))
        next_id = self.conn.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM warnings WHERE account_id = ?', (self.user[0],)).fetchone()[0]

        self.conn.execute('INSERT INTO warnings (id, account_id, reason) VALUES (?, ?, ?)', (next_id, self.user[0], reason))

        if next_id >= 3:
            self.conn.execute(f'UPDATE accounts SET banned = 1 WHERE id = {self.user[0]};')

        self.conn.commit()
        self.conn.close()
        exit(0)
