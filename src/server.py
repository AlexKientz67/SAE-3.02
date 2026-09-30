import socket
from threading import Thread

HOST = "0.0.0.0"
PORT = 6000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


## truc magique
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen()

print(f"Serveur en écoute sur {HOST}:{PORT}")

"""
while True:
    client, address = server.accept()
    print(f"Connexion acceptée depuis {address}")

    data = client.recv(1024)

    print(f"Reçu du client : {data.decode()}")

    if data.decode().strip() == "PING":
        client.sendall(b"OK\n")
"""

carrefour = None
numero_voiture = 0
phase_feu = 0


def client_thread(client, nbr_voiture):

    global carrefour
    global phase_feu

    while True:
        data = client.recv(1024)

        if not data:
            print("close connection")
            if carrefour is not None:
                carrefour.sendall(f"{nbr_voiture}|deco\n".encode())
            break

        print(data.decode())

        message = data.decode().strip()

        if message == "PING":
            client.sendall(b"OK\n")
        elif message == "carrefour":
            carrefour = client
            print("Carrefour registred")
        elif message.startswith("phase-feu"):
            phase_feu = message.split(",")[1]
        elif message == "GET_FEU":
            client.sendall(f"{phase_feu}".encode())
        else:
            if carrefour is not None:
                carrefour.sendall(
                    f"{nbr_voiture}|{message}\n".encode()
                )



while True:
    client, address = server.accept()

    numero_voiture += 1

    print("nouvelle_connexion :", address)
    Thread(target=client_thread, args=(client,numero_voiture)).start()