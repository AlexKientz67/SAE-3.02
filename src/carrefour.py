import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QTimer
import socket


class FenetreCarrefour(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE 3.02 - ProxmoxVE")
        self.setGeometry(100, 100, 800, 800)

        # Scène
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 800)

        self.vue = QGraphicsView(self.scene)
        self.setCentralWidget(self.vue)

        self.scene.setBackgroundBrush(
            QBrush(QColor("white"))
        )

        # CO Serveur
        HOST = "127.0.0.1"
        PORT = 6000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.sock.sendall(b"carrefour\n")
        self.sock.setblocking(False)
        print("Connecté au serveur")

        # Timer Serveur
        self.timer_serveur = QTimer(self)
        self.timer_serveur.timeout.connect(self.recevoir_serveur)
        self.timer_serveur.start(20)

        # Gestion voiture

        self.voitures = {}


        # Routes
        route = QBrush(QColor(50, 50, 50))
        sans_bordure = QPen(Qt.PenStyle.NoPen)

        self.scene.addRect(
            330, 0, 140, 800,
            sans_bordure,
            route
        )

        self.scene.addRect(
            0, 330, 800, 140,
            sans_bordure,
            route
        )

        # Feux
        self.feux = []

        for x, y in [
            (340, 290),
            (440, 480),
            (310, 440),
            (480, 340)
        ]:
            self.feux.append(
                self.scene.addEllipse(
                    x,
                    y,
                    20,
                    20,
                    sans_bordure,
                    QBrush(QColor("red"))
                )
            )

        self.phase_feu = 0

        # Timer des feux
        self.timer_feux = QTimer(self)
        self.timer_feux.timeout.connect(self.changer_feux)
        self.timer_feux.start(5000)

        self.changer_feux()

    def recevoir_serveur(self):

        try:
            data = self.sock.recv(1024)

            if not data:
                print("Erreur de connexion")
                self.timer_serveur.stop()
                return

            message = data.decode().strip()
            print(message)

            # Sépare le numéro du client du message
            numero, message = message.split("|", 1)

            if message.startswith("Vehicule"):

                decoupage = message.split(",")

                x = int(decoupage[0].split()[1])
                y = int(decoupage[1])
                direction = decoupage[2].strip()

                print("Voiture", numero, ":", x, y, direction)

                if numero not in self.voitures:
                    self.voitures[numero] = self.scene.addRect(
                        0,
                        0,
                        20,
                        20,
                        QPen(Qt.PenStyle.NoPen),
                        QBrush(QColor("blue"))
                    )
                # Déplacer la voiture
                self.voitures[numero].setPos(x, y)
            elif message.startswith("deco"):
                if numero in self.voitures:
                    voiture = self.voitures.pop(numero)
                    self.scene.removeItem(voiture)
                    print("Voiture", numero, "supprimé")

        except BlockingIOError:
            pass


    def changer_feux(self):

        if self.phase_feu == 0:
            vertical = "vert"
            horizontal = "rouge"

        elif self.phase_feu == 1:
            vertical = "orange"
            horizontal = "rouge"

        elif self.phase_feu == 2:
            vertical = "rouge"
            horizontal = "vert"

        else:
            vertical = "rouge"
            horizontal = "orange"

        # Les deux premiers feux sont verticaux
        for i in range(4):

            if i < 2:
                couleur = vertical
            else:
                couleur = horizontal

            if couleur == "vert":
                pinceau = QBrush(QColor("green"))

            elif couleur == "orange":
                pinceau = QBrush(QColor("orange"))

            else:
                pinceau = QBrush(QColor("red"))

            self.feux[i].setBrush(pinceau)

        self.phase_feu += 1

        if self.phase_feu == 4:
            self.phase_feu = 0

        self.sock.sendall(f"phase-feu,{self.phase_feu}".encode())


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetreCarrefour()
    fenetre.show()

    sys.exit(app.exec())