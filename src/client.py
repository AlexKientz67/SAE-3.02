from threading import Thread, Event
import socket
import time

HOST = "127.0.0.1"
PORT = 6000

"""

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

client.sendall(b"Bonjour\n")

data = client.recv(1024)

print(f"Réponse du serveur : {data.decode()}")



client.close()
"""

def get_spawn_point_x(direction : str) -> int:
    if direction == "bas":
        return 340
    elif direction == "haut":
        return 440
    elif direction == "droite":
        return 0
    elif direction == "gauche":
        return 800

def get_spawn_point_y(direction : str) -> int:
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

    def test_connexion(self, sock : socket.socket) -> int:
        sock.sendall(b"PING\n")
        data = sock.recv(1024).decode().strip()

        if data == "OK":
            print("Serveur disponible")
            return 1
        else:
            print("Serveur indisponible...")
            return 0

    def run(self):
        with self.create_connexion() as sock:
            if self.test_connexion(sock) == 1:
                while True:
                    sock.sendall(b"GET_FEU\n")

                    data = sock.recv(1024).decode().strip()

                    feu = data

                    print("Feu :", feu)

                    sock.sendall(f"Vehicule {self.x}, {self.y}, {self.direction}\n".encode())
                    time.sleep(0.005)

                    if self.direction == "bas":
                        if self.y == 265 and feu != "1":
                            print("stop")
                        else:
                            self.avancer()
                        if self.y > 850:
                            break

                    if self.direction == "haut":
                        if self.y == 512 and feu != "1":
                            print("stop")
                        else:
                            self.avancer()
                        if self.y < -50:
                            break

                    if self.direction == "droite":
                        if self.x == 270 and feu != "3":
                            print("stop")
                        else:
                            self.avancer()
                        if self.x > 850:
                            break

                    if self.direction == "gauche":
                        if self.x == 510 and feu != "3":
                            print("stop")
                        else:
                            self.avancer()
                        if self.x < -50:
                            break



if __name__ == "__main__":
    v1 = Vehicule("bas")

    v1.run()

