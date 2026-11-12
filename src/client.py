from threading import Thread, Event
import socket
import time
import random

HOST = "127.0.0.1"
PORT = 6000


def get_spawn_point_x(direction: str) -> int:
    if direction == "bas":
        return 340
    elif direction == "haut":
        return 440
    elif direction == "droite":
        return 0
    elif direction == "gauche":
        return 800


def get_spawn_point_y(direction: str) -> int:
    if direction == "bas":
        return 0
    elif direction == "haut":
        return 800
    elif direction == "droite":
        return 440
    elif direction == "gauche":
        return 340


class Vehicule():
    def __init__(self, direction="bas"):
        self.__x = get_spawn_point_x(direction)
        self.__y = get_spawn_point_y(direction)
        self.__direction = direction
        self.peut_avacer = 1
        self.feu_passe = False

        """La voiture peut choisir son itinéraire , cerveau"""
        choix_trajet = ["tout_droit", "tourner_droite"]
        self.action = random.choice(choix_trajet)

    def avancer(self):
        if self.__direction == "bas":
            self.__y += 1
        elif self.__direction == "haut":
            self.__y -= 1
        elif self.__direction == "droite":
            self.__x += 1
        elif self.__direction == "gauche":
            self.__x -= 1

    @property
    def x(self) -> int:
        return self.__x

    @x.setter
    def x(self, value: int):
        self.__x = value

    @property
    def y(self) -> int:
        return self.__y

    @y.setter
    def y(self, value: int):
        self.__y = value

    @property
    def direction(self) -> str:
        return self.__direction

    def create_connexion(self) -> socket.socket:
        return socket.create_connection((HOST, PORT))

    def test_connexion(self, sock: socket.socket) -> int:
        sock.sendall(b"PING\n")

        data = sock.recv(1024).decode().strip()

        if data == "OK":
            return 1
        else:
            return 0

    def run(self):
        with self.create_connexion() as sock:

            if self.test_connexion(sock) == 1:

                while True:

                    # Récupération du feu
                    sock.sendall(b"GET_FEU\n")

                    data = sock.recv(1024).decode().strip()

                    feu = data

                    # Envoi de la position au serveur
                    sock.sendall(
                        f"Vehicule {self.x}, {self.y}, {self.direction}\n".encode()
                    )

                    # Réponse du serveur concernant la collision
                    collision = sock.recv(1024).decode().strip()

                    if collision == "STOP":
                        time.sleep(0.005)
                        continue

                    time.sleep(0.005)

                    if self.direction == "bas":

                        if self.y == 265 and feu != "1" and feu != "98":
                            pass
                        else:
                            if self.action == "tourner_droite" and self.y == 340:
                                self.__direction = "gauche"

                            self.avancer()

                        if self.y > 850:
                            break

                    elif self.direction == "haut":

                        if self.y == 512 and feu != "1" and feu != "98":
                            pass
                        else:
                            if self.action == "tourner_droite" and self.y == 440:
                                self.__direction = "droite"
                            self.avancer()

                        if self.y < -50:
                            break

                    elif self.direction == "droite":

                        if self.x == 270 and feu != "3" and feu != "98":
                            pass
                        else:
                            if self.action == "tourner_droite" and self.x == 340:
                                self.__direction = "bas"
                            self.avancer()

                        if self.x > 850:
                            break

                    elif self.direction == "gauche":

                        if self.x == 510 and feu != "3" and feu != "98":
                            pass
                        else:
                            if self.action == "tourner_droite" and self.x == 440:
                                self.__direction = "haut"
                            self.avancer()

                        if self.x < -50:
                            break


if __name__ == "__main__":

    v1 = Vehicule("gauche")

    v1.run()