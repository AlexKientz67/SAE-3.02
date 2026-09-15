import select
import socket


DISTANCE = 10
ARRETS = {"bas": 240, "haut": 510, "droite": 260, "gauche": 510}


def rectangle(position):
    x, y, direction = position
    if direction == "bas" or direction == "haut":
        largeur = 20
        hauteur = 40
    else:
        largeur = 40
        hauteur = 20
    return x, y, x + largeur, y + hauteur


def trop_proche(position, autre):
    x1, y1, x2, y2 = rectangle(position)
    a1, b1, a2, b2 = rectangle(autre)
    # Pas de risque si les rectangles sont assez éloignés sur un des axes.
    if x1 >= a2 + DISTANCE or a1 >= x2 + DISTANCE:
        return False
    if y1 >= b2 + DISTANCE or b1 >= y2 + DISTANCE:
        return False
    return True


def engagee(position):
    x, y, direction = position
    if direction in ("bas", "haut"):
        return 240 < y < 510
    return 260 < x < 510


def position_autorisee(position, ancienne, autres, vertical, horizontal):
    x, y, direction = position
    axe_vertical = direction in ("bas", "haut")
    if ancienne is None:
        # Reculer une nouvelle voiture jusqu'à trouver une place libre.
        place_libre = False
        while not place_libre:
            place_libre = True
            for autre in autres:
                if trop_proche((x, y, direction), autre):
                    place_libre = False
                    break
            if not place_libre:
                if direction == "bas":
                    y -= 50
                elif direction == "haut":
                    y += 50
                elif direction == "droite":
                    x -= 50
                else:
                    x += 50
        return x, y, direction

    if axe_vertical:
        coordonnee = ancienne[1]
        suivante = y
        couleur = vertical
    else:
        coordonnee = ancienne[0]
        suivante = x
        couleur = horizontal

    limite = ARRETS[direction]
    entre = False
    if direction == "bas" or direction == "droite":
        if coordonnee <= limite and suivante > limite:
            entre = True
    else:
        if coordonnee >= limite and suivante < limite:
            entre = True

    # Attendre que les voitures de l'autre axe aient fini de traverser.
    conflit = False
    for autre in autres:
        autre_verticale = autre[2] == "bas" or autre[2] == "haut"
        if autre_verticale != axe_vertical and engagee(autre):
            conflit = True
            break

    if entre:
        if couleur != "vert" or conflit:
            if axe_vertical:
                y = limite
            else:
                x = limite

    position = (x, y, direction)
    for autre in autres:
        if trop_proche(position, autre):
            return ancienne
    return position


def diffuser(message, clients):
    for connexion, infos in list(clients.items()):
        if infos["carrefour"]:
            try:
                connexion.sendall(message.encode())
            except OSError:
                # La boucle du serveur traitera la déconnexion à la lecture.
                pass


def deconnecter(connexion, clients, feux):
    infos = clients.pop(connexion)
    connexion.close()
    if infos["position"] is not None:
        diffuser(f"depart,{infos['id']}\n", clients)
    if infos["carrefour"]:
        feux = ("rouge", "rouge")
    return feux


def lancer_serveur():
    clients = {}
    prochain_id = 0
    feux = ("rouge", "rouge")

    with socket.socket() as serveur:
        serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serveur.bind(("127.0.0.1", 5500))
        serveur.listen()
        try:
            while True:
                prets, _, _ = select.select([serveur] + list(clients), [], [])
                for client in prets:
                    if client == serveur:
                        connexion, _ = serveur.accept()
                        connexion.settimeout(0.5)
                        clients[connexion] = {
                            "id": prochain_id, "carrefour": False,
                            "position": None, "coordonnees": None, "tampon": b"",
                        }
                        prochain_id += 1
                        continue
                    if client not in clients:
                        continue
                    try:
                        donnees = client.recv(4096)
                        if not donnees:
                            feux = deconnecter(client, clients, feux)
                            continue
                        infos = clients[client]
                        infos["tampon"] += donnees
                        # TCP peut regrouper ou découper les lignes.
                        while b"\n" in infos["tampon"]:
                            ligne, infos["tampon"] = infos["tampon"].split(b"\n", 1)
                            message = ligne.decode()
                            if message == "carrefour":
                                infos["carrefour"] = True
                                for voiture in clients.values():
                                    if voiture["position"]:
                                        client.sendall(voiture["position"].encode())
                            elif infos["carrefour"]:
                                type_message, vertical, horizontal = message.split(",")
                                if type_message == "feux" and vertical in ("rouge", "orange", "vert") and horizontal in ("rouge", "orange", "vert"):
                                    feux = (vertical, horizontal)

                            else:
                                x, y, direction = message.split(",")
                                if direction not in ("bas", "haut", "droite", "gauche"):
                                    continue
                                vertical, horizontal = feux
                                autres = []
                                for connexion, voiture in clients.items():
                                    if connexion != client:
                                        if voiture["coordonnees"] is not None:
                                            autres.append(voiture["coordonnees"])
                                x, y, direction = position_autorisee(
                                    (int(x), int(y), direction), infos["coordonnees"],
                                    autres, vertical, horizontal)
                                infos["coordonnees"] = (x, y, direction)
                                position = f"position,{infos['id']},{x},{y},{direction}\n"
                                infos["position"] = position
                                diffuser(position, clients)
                                client.sendall(f"accord,{x},{y}\n".encode())
                    except (OSError, ValueError):
                        feux = deconnecter(client, clients, feux)
        except KeyboardInterrupt:
            pass
        finally:
            for connexion in clients:
                connexion.close()


if __name__ == "__main__":
    lancer_serveur()
