import socket
from threading import Thread, Event


class Vehicule(Thread):
    def __init__(self, x, y, direction="bas"):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.vitesse = 3
        self.arret = Event()

    def arreter(self):
        self.arret.set()

    def avancer(self):
        if self.direction == "bas":
            self.y += self.vitesse
        elif self.direction == "haut":
            self.y -= self.vitesse
        elif self.direction == "droite":
            self.x += self.vitesse
        else:
            self.x -= self.vitesse

    def run(self):
        try:
            with socket.create_connection(("127.0.0.1", 5500), timeout=2) as connexion:
                with connexion.makefile("r") as reception:
                    while not self.arret.is_set():
                        connexion.sendall(f"{self.x},{self.y},{self.direction}\n".encode())
                        # Attendre la position validée : le serveur garde les distances.
                        ligne = reception.readline()
                        if not ligne:
                            break
                        _, x, y = ligne.strip().split(",")
                        self.x, self.y = int(x), int(y)
                        if self.arret.wait(0.05):
                            break
                        self.avancer()
        except OSError as erreur:
            print("Connexion au serveur interrompue :", erreur)


if __name__ == "__main__":
    try:
        Vehicule(340, 0).run()
    except KeyboardInterrupt:
        pass
