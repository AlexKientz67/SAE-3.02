import socket
from threading import Thread
import time


HOST = "0.0.0.0"
PORT = 6000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Permet de réutiliser le port rapidement
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen()

print(f"Serveur en écoute sur {HOST}:{PORT}")


carrefour = None
numero_voiture = 0
phase_feu = 0

positions_voitures = {}

def collision(nbr_voiture, message):

    try:
        # Exemple :
        # Vehicule 340, 250, bas

        partie = message.split(" ", 1)[1].split(",")

        x = int(partie[0].strip())
        y = int(partie[1].strip())

        # Vérifie toutes les autres voitures
        for numero, position in positions_voitures.items():

            # On ne compare pas la voiture avec elle-même
            if numero != nbr_voiture:

                autre_x, autre_y = position

                # Distance entre les deux voitures
                if abs(x - autre_x) < 40 and abs(y - autre_y) < 40:

                    return True

        # Pas de collision :
        # on enregistre la nouvelle position
        positions_voitures[nbr_voiture] = (x, y)

    except Exception as e:
        return True

    return False


def client_thread(client, nbr_voiture):

    global carrefour
    global phase_feu

    while True:
        data = client.recv(1024)

        if not data:

            print("close connection")

            # Supprime la voiture des positions
            if nbr_voiture in positions_voitures:
                del positions_voitures[nbr_voiture]

            # Informe le carrefour
            if carrefour is not None:
                carrefour.sendall(
                    f"{nbr_voiture}|deco\n".encode()
                )

            break

        message = data.decode().strip()

        if message == "PING":

            client.sendall(b"OK\n")

        elif message == "carrefour":

            carrefour = client

            print("Carrefour registred")

        # PHASE DU FEU
        elif message.startswith("phase-feu"):

            phase_feu = message.split(",")[1]

        # DEMANDE DU FEU
        elif message == "GET_FEU":

            client.sendall(
                f"{phase_feu}".encode()
            )

        # VEHICULE
        else:
            if message.startswith("Vehicule"):
                # Vérification collision
                if collision(nbr_voiture, message):
                    client.sendall(b"STOP\n")
                    continue
                else:
                    client.sendall(b"OK\n")

                # Envoie la position au carrefour
                if carrefour is not None:
                    carrefour.sendall(f"{nbr_voiture}|{message}\n".encode())

            if message.startswith("Urgence"):
                if collision(nbr_voiture, message):
                    client.sendall(b"STOP\n")
                    continue

                else:
                    client.sendall(b"OK\n")
                if carrefour is not None:
                    carrefour.sendall(f"{nbr_voiture}|{message}\n".encode())

while True:
    client, address = server.accept()
    numero_voiture += 1
    print("nouvelle_connexion :",address)
    Thread(
        target=client_thread,
        args=(client, numero_voiture)
    ).start()
