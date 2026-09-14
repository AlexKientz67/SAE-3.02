import socket
from threading import Thread, Event


class Vehicule(Thread):
    def __init__(self, x, y, direction):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.vitesse = 3
        self.arret = Event()

    def arreter(self):
        self.arret.set()

    def run(self):
        connexion = socket.create_connection(("127.0.0.1", 5500))

        while not self.arret.is_set():
            connexion.sendall(f"{self.x},{self.y}\n".encode())

            if self.direction == "bas":
                self.y += self.vitesse

            elif self.direction == "haut":
                self.y -= self.vitesse

            elif self.direction == "droite":
                self.x += self.vitesse

            else:
                self.x -= self.vitesse

            self.arret.wait(0.05)

        connexion.close()


if __name__ == "__main__":
    try:
        Vehicule(340, 0).run()
    except KeyboardInterrupt:
        pass
