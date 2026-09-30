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
positions = {}


def client_thread(client, nbr_voiture):

    global carrefour
    global phase_feu
    global positions

    while True:
        data = client.recv(1024)

        if not data:
            print("close connection")

            if nbr_voiture in positions:
                del positions[nbr_voiture]

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

            stop = 0

            x, y, direction = positions.get(
                nbr_voiture,
                (0, 0, "")
            )

            for numero, (x2, y2, direction2) in positions.items():

                if numero == nbr_voiture:
                    continue

                if direction != direction2:
                    continue

                if direction == "bas" and 0 < y2 - y < 30:
                    stop = 1

                elif direction == "haut" and 0 < y - y2 < 30:
                    stop = 1

                elif direction == "droite" and 0 < x2 - x < 30:
                    stop = 1

                elif direction == "gauche" and 0 < x - x2 < 30:
                    stop = 1

            client.sendall(f"{phase_feu}|{stop}\n".encode())
        else:

            # Message d'une voiture
            if message.startswith("Vehicule"):
                decoupage = message.split(",")

                x = int(decoupage[0].split()[1])
                y = int(decoupage[1])
                direction = decoupage[2].strip()

                # Enregistre la position
                positions[nbr_voiture] = (
                    x,
                    y,
                    direction
                )

            # Envoie le message au carrefour
            if carrefour is not None:
                carrefour.sendall(
                    f"{nbr_voiture}|{message}\n".encode()
                )



while True:
    client, address = server.accept()

    numero_voiture += 1

    print("nouvelle_connexion :", address)
    Thread(target=client_thread, args=(client,numero_voiture)).start()