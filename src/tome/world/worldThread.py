from . import map as m
import sending as sending
import utils.logging as log

global maps
maps = {
    'overworld': m.Map.from_config("OVERWORLD")
}
print(maps["overworld"])

def worldThread():
    while True:
        recv = sending.receive("World")
        if type(recv) == sending.Message:
            if type(recv.message) != dict or list(recv.message.keys()) != ["command","data"]:
                log.warn(f"Got a message from: {recv.sender_id} that wasnt the right format: {recv.message}",name="World")
            else:
                match recv.message["command"]:
                    case "get_map":
                        if list(recv.message["data"].keys()) != ["map","roomid","x","y"]:
                            log.warn(f"Got a message from: {recv.sender_id} that wasnt the right format: {recv.message}",name="World")
                        elif recv.message["data"]["map"] not in maps.keys():
                            log.warn(f"{recv.sender_id} tried to access unknown map: {recv.message['data']['map']}",name="World")
                        else:
                            msg = sending.Message(recv.sender_id,"World",maps[recv.message["data"]["map"]].get_room(recv.message["data"]["roomid"]))
                            sending.send(msg)
