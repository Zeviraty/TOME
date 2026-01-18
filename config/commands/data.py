import tome.sending as sending

def map(client,arguments):
    msg = sending.Message("World",client.td,{"command":"get_map","data":{"map":"Overworld","x":0,"y":0}})
    sending.send(msg)
    msg = sending.receive_block(client.td)
    client.send(msg)
