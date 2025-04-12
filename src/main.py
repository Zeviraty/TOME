import socket
import threading
import banners
from player import Player

clients: list[Player] = []

def handle_client(client_socket, addr):
    client = Player(client_socket, addr)
    clients.append(client)
    client.send(banners.generate("TOME"))
    client.send("Welcome to TOME!")

def main():
    while True:
        client, addr = server.accept()
        print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,addr))
        try:
            client_handler.start()
        except BrokenPipeError:
            print(f"[+] {addr[0]}:{addr[1]} broke pipe" )

if __name__ == "__main__":
    bind_ip = "0.0.0.0"
    bind_port = 2323
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print(f"[+] Listening on port {bind_ip} : {bind_port}")
    try:
        main()
    except KeyboardInterrupt:
        print("Closing server...")
        for client in clients:
            client.disconnect("Server closed by admin.")
