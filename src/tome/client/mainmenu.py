import hashlib
from tome.utils.color import *
import tome.utils.logging as log
import tome.utils.config as config
import tome.client.telnet as telnet
from tome.client.client import Client

def racemenu(client: Client) -> str | dict[str, str | None]:
    '''
    Shows a menu to select a race for a character

    Parameters
    ----------
    client : Client
        Client to show menu to
    '''
    races = {entry['name']: entry['subs'] for entry in config.get_dir("races",ls=True)}
    keys = list(races.keys())
    keys.append("Back")
    race: str = str(client.menu(
        keys,
        "\nRace",
        string=True
    ))
    if race == "Back":
        return "Back"
    else:
        if len(races[race]) > 0:
            sub_races = races[race]
            sub_races.append("Back")
            sub_race: str | None = str(client.menu(
                sub_races,
                "\nSub-Race",
                string=True
            ))
            if sub_race == "Back":
                return racemenu(client)
            else:
                return {"sub_race": sub_race,"race":race}
        else:
            sub_race: str | None = None
            return {"sub_race": sub_race, "race":race}


def mainmenu(client: Client) -> None:
    '''
    Shows the main menu to a Client

    Parameters
    ----------
    client : Client
        Client to show main menu to
    '''
    while True:
        if client.disconnected:
            return
        if client.user != None and len(client.user) == 0:
            client.disconnect()
            return
        selected = client.menu(
            [
                "New character",
                "List characters",
                "Exit",
            ],
            "Main Menu",
            "Command or Name of character: ",
            True,
        )
        match selected:
            case 0:
                client.send("New character\n")
                menus = [
                    {"name":"Class","type":"options","options":config.get_dir("classes",key="name",ls=True)},
                    {"name":"Race","type":"custom","function":racemenu},
                    {"name":"Name","type":str},
                    {"name":"Gender","type":"options","options":["Male","Female","Non-Binary"]},
                    {"name":"Alignment 1","type":"options","options":["lawful","neutral","chaotic"]},
                    {"name":"Alignment 2","type":"options","options":["good","neutral","evil"]},
                ]

                recv = client.pmenu(menus)



                client.character_data["Class"] = recv["Class"]
                client.character_data["Sub-race"] = recv["sub_race"]
                client.character_data["Race"] = recv["race"]
                client.character_data["Name"] = recv["Name"]
                client.character_data["Gender"] = recv["Gender"]
                client.character_data["A1"] = recv["Alignment 1"]
                client.character_data["A2"] = recv["Alignment 2"]

                client.character_data["ID"] = client.conn.execute("INSERT INTO characters (name, account_id) VALUES (?,?) RETURNING id;",(recv["Name"],client.user[0])).fetchone()[0]

                for k,v in client.character_data.items():
                    if k == "Name" or k == "ID":
                        continue
                    client.conn.execute("INSERT INTO character_attributes (attr_name, attr_value, character_id) VALUES (?,?,?)",(k,v,client.character_data["ID"]))

                client.conn.commit()
                if client.yn("Play as "+recv["Name"]+"? "):
                    client.send()
                    break
            case 1:
                client.send("")
                characters = client.conn.execute("SELECT * FROM characters WHERE account_id = ?;",(client.user[0],)).fetchall()
                if len(characters) != 0:
                    client.send(YELLOW.fg()+Color(17).apply("Characters:                 ",bg=True)+DARK_BLUE.bg())
                    for character in characters:
                        client.send(f"{character[1]} {' ' * (22 - len(character[1]) - len(str(character[3])))}lvl: {character[3]}")
                else:
                    client.send(YELLOW.fg()+"You have no characters yet, create one!")
                client.send(RESET)
            case 2:
                client.disconnect("You chose to exit this realm.")
                break
            case _:
                characters = client.conn.execute("SELECT name, id FROM characters WHERE account_id = ?;",(client.user[0],)).fetchall()
                if selected in [item[0] for item in characters]:
                    id = [item[1] if item[0] == selected else False for item in characters]
                    while False in id:
                        id.remove(False)
                    attributes = client.conn.execute("SELECT * FROM character_attributes WHERE character_id = ?;",(id[0],)).fetchall()
                    client.character_data['attributes'] = attributes
                    break
                else:
                    client.send("Not the name of a character or a command.")

def login(client: Client, player:str|None=None,gmcp:bool = True, amount: int = 0,askpassword: bool = False) -> None:
    '''
    Login sequence for a Client

    Parameters
    ----------
    client : Client
        Client to log in
    player : str|None, optional
        Username of client (default is None)
    gmcp : bool, optional
        If gmcp should be enabled (default is True)
    amount : int, optional
        Amount of tries that have occurred (default is 0)
    askpassword : bool
        If there should be asked for a new password (default is False)
    '''
    if client.disconnected:
        return
    if amount > 5:
        client.disconnect()
        return
    if gmcp:
        telnet.send(client,"IAC WILL GMCP")
        gmcp_response = telnet.get(client)
        if "gmcp" in gmcp_response.keys():
            client.gmcp = gmcp_response["gmcp"]
            client.mudclient = {"client": "UNKNOWN"} 
        if "Core.Hello" in gmcp_response.keys():
            client.mudclient = gmcp_response["Core.Hello"]

    if player == None:
        username = client.input("Username:").lower()
    else:
        username = player
    passwords = client.conn.execute("SELECT password FROM accounts WHERE name = ?;",(username,)).fetchone()

    if player != None:
        if not passwords and askpassword:
            password = client.input(f"New password for {player}: ",echo=False)
            client.conn.execute("INSERT INTO accounts (name, password) VALUES (?, ?)", (player,str(hashlib.sha256(password.encode()).digest())))
            client.conn.commit()
        client.username = username
        client.user = client.conn.execute("SELECT * FROM accounts WHERE name = ?;",(username,)).fetchone()
        log.info(f"Logged in as: {client.username}",name=str(client.td))
        client.td = client.username
        if askpassword:
            privileges = client.conn.execute("SELECT privilege FROM account_privileges WHERE account_id = ?;",(client.user[0],)).fetchall()
            for i in privileges:
                client.privileges.append(i[0])
        return

    if passwords:
        password = client.input("Password: ",echo=False)

        if str(hashlib.sha256(password.encode()).digest()) == passwords[0]:
            if client.conn.execute("SELECT banned FROM accounts WHERE name = ?;",(username,)).fetchone()[0] == 1:
                client.disconnect("You have been banned.")
                client.conn.close()
                exit(0)
            client.send(f"Logged in as: {username}.\n")
            client.username = username
            client.user = client.conn.execute("SELECT * FROM accounts WHERE name = ?;",(username,)).fetchone()
            log.info(f"Logged in as: {client.username}",name=str(client.td))
            client.td = client.username
            privileges = client.conn.execute("SELECT privilege FROM account_privileges WHERE account_id = ?;",(client.user[0],)).fetchall()
            for i in privileges:
                client.privileges.append(i[0])
        else:
            client.send("Wrong password.")
            login(client, gmcp=False, amount= amount + 1)

    else:
        create = client.yn("Account does not exist, do you want to create it? ",preferred_option="n")
        if create:
            while True:
                password = client.input("Password: ",echo=False)
                if password == client.input("Confirm password: ",echo=False):
                    break
                else:
                    client.send("Passwords do not match.")

            client.conn.execute("INSERT INTO accounts (name, password) VALUES (?, ?)",
                (
                    username,
                    str(hashlib.sha256(password.encode()).digest())
                )
            )

            client.conn.commit()

        login(client,gmcp=False, amount = amount + 1)

