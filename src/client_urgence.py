import socket
import time

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


class Vehicule_Urgence():

    def __init__(self, direction="bas", *, host, port):
        self.host = host
        self.port = port
        self.__x = get_spawn_point_x(direction)
        self.__y = get_spawn_point_y(direction)
        self.__direction = direction
        self.peut_avacer = 1
        self.feu_passe = False

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
        return socket.create_connection((self.host, self.port))

    def test_connexion(self, sock: socket.socket) -> int:

        sock.sendall(b"PING\n")

        data = sock.recv(1024).decode().strip()

        if data == "OK":
            return 1
        else:
            return 0

    def run(self):
        """Fait avancer l’ambulance jusqu’à sa sortie en respectant les arrêts imposés par le serveur."""

        with self.create_connexion() as sock:

            if self.test_connexion(sock) == 1:

                decalage = False

                while True:

                    sock.sendall(
                        f"Urgence {self.x}, {self.y}, {self.direction}\n".encode()
                    )

                    collision = sock.recv(1024).decode().strip()

                    if collision == "STOP":
                        time.sleep(0.005)
                        continue

                    self.avancer()

                    time.sleep(0.005)

                    if self.direction == "bas":
                        if self.y > 850:
                            break

                    elif self.direction == "haut":
                        if self.y < -50:
                            break

                    elif self.direction == "droite":
                        if self.x > 850:
                            break

                    elif self.direction == "gauche":
                        if self.x < -50:
                            break
