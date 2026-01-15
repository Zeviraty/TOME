import tome.utils.import_lib as il
import tome.utils.config as conf
import tome.utils.logging as log
import re

def parse_command(cmd, client):
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
        module = il.load_module(f"config/commands/{mod.split('.')[0]}.py")
        module.__getattribute__(mod.split('.')[1])(client=client,arguments=args)
    except Exception as e:
        client.send(f"Error loading command: {cmd}")
        log.error(f"Error loading command: {cmd}:\n{e}",name=client.td)
        return

def play(client):
    while not client.disconnected:
        cmd = client.input()
        parse_command(cmd,client)
