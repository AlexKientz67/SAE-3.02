import select
import socket


def lancer_serveur():
    clients = {}
    id = 0

    serveur = socket.socket()
    serveur.bind(("127.0.0.1", 5500))
    serveur.listen()

    while True:
        prets, _, _ = select.select([serveur] + list(clients), [], [])

        for client in prets:

            if client == serveur:
                connexion, _ = serveur.accept()
                clients[connexion] = {
                    "id": id,
                    "carrefour": False,
                    "position": None
                }
                id += 1

            else:
                message = client.recv(4096).decode().strip()

                if not message:
                    client.close()
                    del clients[client]
                    continue

                if message == "carrefour":
                    clients[client]["carrefour"] = True

                    for voiture in clients.values():
                        if voiture["position"]:
                            client.sendall(voiture["position"].encode())

                else:
                    x, y = message.split(",")

                    position = f"position,{clients[client]['id']},{x},{y}\n"
                    clients[client]["position"] = position

                    for autre in clients:
                        if clients[autre]["carrefour"]:
                            autre.sendall(position.encode())


if __name__ == "__main__":
    lancer_serveur()