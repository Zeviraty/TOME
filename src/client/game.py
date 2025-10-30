import sending

def parse_command(cmd, client):
    match cmd:
        case "map":
            msg = sending.Message("World",client.td,{"command":"get_map","data":{"x":0,"y":0,"z":0,"layer":0}})
            sending.send(msg)

def play(client):
    while not client.disconnected:
        cmd = client.input()
        parse_command(cmd,client)
