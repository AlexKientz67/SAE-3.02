import json
import select
import socket


def lancer_serveur():
    clients = {}
    prochain_identifiant = 0

    def envoyer(connexion, message):
        connexion.sendall((json.dumps(message) + "\n").encode())

    def diffuser(message):
        for connexion, client in list(clients.items()):
            if client["carrefour"]:
                try:
                    envoyer(connexion, message)
                except OSError:
                    deconnecter(connexion)

    def deconnecter(connexion):
        client = clients.pop(connexion, None)
        connexion.close()
        if client and client["position"] is not None:
            diffuser({"type": "depart", "id": client["id"]})

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serveur:
        serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serveur.bind(("127.0.0.1", 5000))
        serveur.listen()
        print("Serveur en écoute sur 127.0.0.1:5000", flush=True)
        try:
            while True:
                prets, _, _ = select.select([serveur, *clients], [], [])
                for connexion in prets:
                    if connexion is serveur:
                        nouveau, _ = serveur.accept()
                        nouveau.settimeout(0.5)
                        clients[nouveau] = {
                            "id": prochain_identifiant, "tampon": b"",
                            "carrefour": False, "position": None,
                        }
                        prochain_identifiant += 1
                        continue
                    if connexion not in clients:
                        continue
                    try:
                        donnees = connexion.recv(4096)
                        if not donnees:
                            deconnecter(connexion)
                            continue
                        client = clients[connexion]
                        client["tampon"] += donnees
                        while b"\n" in client["tampon"]:
                            ligne, client["tampon"] = client["tampon"].split(b"\n", 1)
                            if ligne == b"carrefour":
                                client["carrefour"] = True
                                for voiture in clients.values():
                                    if voiture["position"] is not None:
                                        envoyer(connexion, voiture["position"])
                            elif not client["carrefour"]:
                                try:
                                    x, y = map(int, ligne.split(b","))
                                    if not (-2147483648 <= x <= 2147483647 and -2147483648 <= y <= 2147483647):
                                        continue
                                except ValueError:
                                    continue
                                message = {"type": "position", "id": client["id"], "x": x, "y": y}
                                client["position"] = message
                                diffuser(message)
                        if len(client["tampon"]) > 4096:
                            deconnecter(connexion)
                    except OSError:
                        deconnecter(connexion)
        except KeyboardInterrupt:
            pass
        finally:
            for connexion in clients:
                connexion.close()


if __name__ == "__main__":
    lancer_serveur()
