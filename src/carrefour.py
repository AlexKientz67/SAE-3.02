import sys
import socket
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QPushButton
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QTimer
from car import Vehicule



class FenetreCarrefour(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE 3.02 - ProxmoxVE")
        self.setGeometry(100, 100, 800, 800)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 800)

        self.vue = QGraphicsView(self.scene)
        self.setCentralWidget(self.vue)

        self.scene.setBackgroundBrush(QBrush(QColor("white")))

        route = QBrush(QColor(50, 50, 50))
        sans_bordure = QPen(Qt.PenStyle.NoPen)

        self.scene.addRect(330, 0, 140, 800, sans_bordure, route)
        self.scene.addRect(0, 330, 800, 140, sans_bordure, route)

        self.feux = []
        for x, y in [(340, 290), (440, 480), (310, 440), (480, 340)]:
            self.feux.append(self.scene.addEllipse(
                x, y, 20, 20, sans_bordure, QBrush(QColor("red"))))
        self.phase_feu = 0

        self.voitures = {}
        self.vehicules = []

        self.bouton_generer = QPushButton("Générer une voiture")
        self.bouton_generer.clicked.connect(self.generer_voiture)
        self.addToolBar("Véhicules").addWidget(self.bouton_generer)

        self.connexion = socket.create_connection(("127.0.0.1", 5500))
        self.connexion.sendall(b"carrefour\n")
        self.tampon = b""
        self.connexion.setblocking(False)

        self.timer_feux = QTimer(self)
        self.timer_feux.timeout.connect(self.changer_feux)
        self.timer_feux.start(5000)
        self.changer_feux()
        self.timer_reseau = QTimer(self)
        self.timer_reseau.timeout.connect(self.recevoir_positions)
        self.timer_reseau.start(20)

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

        # Les deux premiers feux sont sur l'axe vertical.
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
        try:
            self.connexion.sendall(f"feux,{vertical},{horizontal}\n".encode())
        except OSError:
            self.timer_feux.stop()
        self.phase_feu += 1
        if self.phase_feu == 4:
            self.phase_feu = 0

    def generer_voiture(self):
        direction = random.choice(["bas", "haut", "droite", "gauche"])
        if direction == "bas":
            x, y = 340, 0
        elif direction == "haut":
            x, y = 440, 800
        elif direction == "droite":
            x, y = 0, 440
        else:
            x, y = 800, 340

        vehicules_actifs = []
        for voiture in self.vehicules:
            if voiture.is_alive():
                vehicules_actifs.append(voiture)
        self.vehicules = vehicules_actifs
        voiture = Vehicule(x, y, direction)
        self.vehicules.append(voiture)
        voiture.start()

    def recevoir_positions(self):
        try:
            donnees = self.connexion.recv(4096)
        except BlockingIOError:
            return
        except OSError:
            donnees = b""
        if not donnees:
            self.timer_reseau.stop()
            self.bouton_generer.setEnabled(False)
            return
        self.tampon += donnees
        while b"\n" in self.tampon:
            ligne, self.tampon = self.tampon.split(b"\n", 1)
            champs = ligne.decode().split(",")
            if champs[0] == "position":
                _, identifiant, x, y, direction = champs
                self.mettre_a_jour_voiture(int(identifiant), int(x), int(y), direction)
            elif champs[0] == "depart":
                self.retirer_voiture(int(champs[1]))

    def mettre_a_jour_voiture(self, identifiant, x, y, direction):
        if identifiant not in self.voitures:
            couleurs = ["blue", "yellow", "cyan", "magenta"]

            if direction == "droite" or direction == "gauche":
                largeur = 40
                hauteur = 20
            else:
                largeur = 20
                hauteur = 40
            self.voitures[identifiant] = self.scene.addRect(
                0, 0, largeur, hauteur,
                QPen(Qt.PenStyle.NoPen),
                QBrush(QColor(couleurs[identifiant % 4]))
            )

        self.voitures[identifiant].setPos(x, y)

    def retirer_voiture(self, identifiant):
        voiture = self.voitures.pop(identifiant, None)

        if voiture:
            self.scene.removeItem(voiture)

    def closeEvent(self, event):
        for voiture in self.vehicules:
            voiture.arreter()

        for voiture in self.vehicules:
            voiture.join()

        self.timer_reseau.stop()
        self.connexion.close()

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        fenetre = FenetreCarrefour()
    except OSError as erreur:
        print("Connexion impossible :", erreur)
        sys.exit(1)

    fenetre.show()
    sys.exit(app.exec())
