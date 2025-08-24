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

clients: list[Client] = []

def handle_client(client_socket, addr, id,debug):
    client = Client(client_socket, addr, id)
    clients.append(client)
    client.send(RESET)
    client.send(banners.generate("TOME"))
    client.send("Welcome to TOME!\n")
    if not debug:
        mm.login(client)
    else:
        conn = db.get()
        debug_player = os.getenv("TOME_DEBUG_USER", "admin")

        mm.login(client,debug_player)
    mm.mainmenu(client)

def main(server,debug):
    id = 0
    while True:
        client, addr = server.accept()
        log.info(f"Accepted connection from: {addr[0]}:{addr[1]} id: {id + 1}")
        id += 1
        client_handler = threading.Thread(target=handle_client, args=(client,addr,id,debug))
        try:
            client_handler.start()
        except BrokenPipeError:
            log.disconnect(f"{addr[0]}:{addr[1]} broke pipe" )

@click.command()
@click.option('-b','--bind', default="0.0.0.0", help="IP to bind to")
@click.option('-p','--port', default=2323, help="Port for tome")
@click.option('-d','--debug', help="Enable debug mode", is_flag=True)
def cmd(bind = "0.0.0.0", port = 2323, debug=False):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind, port))
    server.listen(5)
    log.info(f"Listening on port {bind} : {port}")
    try:
        main(server,debug)
    except KeyboardInterrupt:
        log.info("Closing server...")
        for client in clients:
            client.disconnect("Server closed by admin.")

if __name__ == "__main__":
    cmd()
