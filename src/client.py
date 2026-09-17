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

class Vehicule():
    def __init__(self, x, y, direction="bas"):
        self.__x = x
        self.__y = y
        self.__direction = direction
        self.peut_avacer = 1

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
                    time.sleep(0.2)

                    if feu == "1":
                        self.avancer()

                    if self.y > 800 or self.y < 0:
                        break


if __name__ == "__main__":
    v1 = Vehicule(100, 50, "bas")

    v1.run()

