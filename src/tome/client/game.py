import tome.utils.import_lib as il
import tome.utils.config as conf
import tome.utils.logging as log
from . import Client
import re

def parse_command(cmd: str, client: Client) -> None:
    '''
    Parses a command inputted by the Client

    Parameters
    ----------
    cmd : str
        Command to be parsed
    client : Client
        Client (used for sending error messages)
    '''
    tokens = []
    for quoted, bare in re.findall(r'"([^"]+)"|(\S+)', cmd):
        tokens.append(quoted or bare)
    cmd = tokens[0]
    args = tokens[1:]
    mod = conf.get("commands/commands.toml", cmd)
    if mod in ("",{},[]):
        client.send(f"Command: {cmd} not found.")
        return
    try:
        if not mod is str:
            log.error("Mod is not a string")
            return
        module = il.load_module(f"config/commands/{mod.split('.')[0]}.py")
        module.__getattribute__(mod.split('.')[1])(client=client,arguments=args)
    except Exception as e:
        client.send(f"Error loading command: {cmd}")
        log.error(f"Error loading command: {cmd}:\n{e}",name=str(client.td))
        return

def play(client: Client):
    '''
    Main game loop

    Parameters
    ----------
    client : Client
        Client for the game loop
    '''
    while not client.disconnected:
        cmd = client.input()
        parse_command(cmd,client)
