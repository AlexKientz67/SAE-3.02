import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt6.QtGui import QColor, QBrush, QPen

import socket
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsTextItem
from PyQt6.QtGui import QColor, QBrush, QPen, QFont

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

        self.panneau_urgence = QGraphicsTextItem("!!! URGENCE : SERREZ A DROITE !!!")
        police = QFont("Arial", 20, QFont.Weight.Bold)
        self.panneau_urgence.setFont(police)
        self.panneau_urgence.setDefaultTextColor(QColor("red"))

        """On le place en haut, centré au dessus du carrefour, visible de n'importe quel intersection"""
        self.panneau_urgence.setPos(120, 50)
        self.scene.addItem(self.panneau_urgence)
        self.panneau_urgence.hide()

        """On crée un bouton d'activation"""
        self.etat_urgence = False
        self.bouton_urgence = QPushButton("Déclencher l'Urgence")
        self.bouton_urgence.clicked.connect(self.basculer_urgence)
        self.addToolBar("Urgence").addWidget(self.bouton_urgence)


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

    def basculer_urgence(self):

        """On inverse l'état (True devient False, et puis inversement)"""
        self.etat_urgence = not self.etat_urgence

        if self.etat_urgence:
            """On allume le panneau"""
            self.panneau_urgence.show()
            self.bouton_urgence.setText("Fin de l'urgence")

            """Le carrefour prévient le serveur de l'urgence avec le sock"""
            self.sock.sendall(b"Urgence, On\n")

        else:
            self.panneau_urgence.hide()
            self.bouton_urgence.setText("Déclencher l'Urgence")

            self.sock.sendall(b"Urgence, OFF \n")

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
            donnees = self.sock.recv(4096)
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

    fenetre = FenetreCarrefour()
    fenetre.show()

    sys.exit(app.exec())