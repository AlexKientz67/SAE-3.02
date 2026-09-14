import socket
from threading import Event, Thread


class Vehicule(Thread):
    def __init__(self, x_depart, y_depart):
        super().__init__()
        self.x = x_depart
        self.y = y_depart
        self.vitesse = 3
        self.arret = Event()

    def arreter(self):
        self.arret.set()

    def run(self):
        # La voiture calcule sa position et l'envoie au serveur.
        try:
            with socket.create_connection(("127.0.0.1", 5000), timeout=2) as connexion:
                while not self.arret.is_set():
                    connexion.sendall(f"{self.x},{self.y}\n".encode("utf-8"))
                    if self.arret.wait(0.05):
                        break
                    self.y += self.vitesse
        except OSError as erreur:
            print(f"Connexion au serveur impossible ou interrompue : {erreur}")


if __name__ == "__main__":
    try:
        Vehicule(340, 0).run()
    except KeyboardInterrupt:
        pass
