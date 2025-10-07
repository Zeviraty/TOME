import socket
import threading
import banners
from utils.color import RESET
import db.utils as db
import utils.logging as log
import click
import os
from client.client import Client
import client.mainmenu as mm
import sending
from world.worldThread import worldThread

clients: list[Client] = []
id = 0

def remove_client(client):
    if client in clients:
        global id
        id -= 1
        clients.remove(client)

def handle_client(client_socket, addr,debug):
    global id
    client = Client(client_socket, addr, id, remove_client, debug)
    clients.append(client)
    client.send(RESET)
    client.send(banners.generate("TOME"))
    client.send("Welcome to TOME!\n")
    if not debug:
        mm.login(client)
    else:
        conn = db.get()
        debug_player = os.getenv("TOME_DEBUG_USER", "admin")

        mm.login(client,debug_player,askpassword=True)
    mm.mainmenu(client)
    remove_client(client)

def main(server,debug):
    global id
    threading.Thread(target=worldThread,daemon=True).start()
    while True:
        client, addr = server.accept()
        log.info(f"Accepted connection from: {addr[0]}:{addr[1]} id: {id + 1}")
        id += 1
        client_handler = threading.Thread(target=handle_client, args=(client,addr,debug),daemon=True)
        try:
            client_handler.start()
        except BrokenPipeError:
            log.disconnect(f"{addr[0]}:{addr[1]} broke pipe" )

@click.command()
@click.option('-b','--bind', default="0.0.0.0", help="IP to bind to")
@click.option('-p','--port', default=2323, help="Port for tome")
@click.option('-d','--debug', help="Enable debug mode", is_flag=True)
def cmd(bind = "0.0.0.0", port = 2323, debug=False):
    log.start()
    sending.init_sender()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind, port))
    server.listen(5)
    log.info(f"Listening on port {bind} : {port}")
    if debug == True:
        log.warn("DEBUG MODE ENABLED")
    try:
        main(server,debug)
    except KeyboardInterrupt:
        log.info("Closing server...")
        for client in clients:
            client.disconnect("Server closed by admin.")
        exit(0)
    except Exception as e:
        log.error("Server crashed with error: "+e)

if __name__ == "__main__":
    cmd()
