import src.world.map as m
import sending
import src.utils.logging as log

global world_map
world_map = m.Map

def worldThread():
    while True:
        recv = sending.receive("World")
        if type(recv) == sending.Message:
            if type(recv.message) != dict or recv.message.keys() != ["command","data"]:
                log.warn(f"Got a message from: {recv.sender_id} that wasnt the right format: {recv.message}","World")
            else:
                match recv.message["command"]:
                    case "get_map":
                        if recv.message["data"].keys() != ["x", "y", "z","layer"]:
                            log.warn(f"Got a message from: {recv.sender_id} that wasnt the right format: {recv.message}","World")
                        else:
                            print("getting map TODO")
        pass
