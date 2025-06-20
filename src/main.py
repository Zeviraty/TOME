import socket
import threading
import banners
from player import Player
from utils.color import RESET
import db
import utils.logging as log

clients: list[Player] = []
global id
id = 0

DEBUG = True

def handle_client(client_socket, addr, id):
    client = Player(client_socket, addr, id)
    clients.append(client)
    client.send(RESET)
    client.send(banners.generate("TOME"))
    client.send("Welcome to TOME!\n")
    if not DEBUG:
        client.login()
    else:
        conn = db.get()
        client.user = conn.execute("SELECT * FROM accounts WHERE name = ?;",("zevvi",)).fetchone()
        client.username = "zevvi"
    client.mainmenu()

def main():
    global id
    while True:
        client, addr = server.accept()
        log.info(f"Accepted connection from: {addr[0]}:{addr[1]} id: {id + 1}")
        id += 1
        client_handler = threading.Thread(target=handle_client, args=(client,addr,id))
        try:
            client_handler.start()
        except BrokenPipeError:
            log.disconnect(f"{addr[0]}:{addr[1]} broke pipe" )

if __name__ == "__main__":
    bind_ip = "0.0.0.0"
    bind_port = 2323
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    log.info(f"Listening on port {bind_ip} : {bind_port}")
    try:
        main()
    except KeyboardInterrupt:
        log.info("Closing server...")
        for client in clients:
            client.disconnect("Server closed by admin.")
