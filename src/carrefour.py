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

import threading
import random

from client_urgence import Vehicule_Urgence as Ambulance

from PyQt6.QtWidgets import QPushButton, QGraphicsTextItem
from PyQt6.QtGui import QFont
from client import Vehicule
from client_urgence import Vehicule_Urgence


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

        self.scene.setBackgroundBrush(QBrush(QColor("#4CAF50")))

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



        """LES ROUTES """
        route = QBrush(QColor(50, 50, 50))
        sans_bordure = QPen(Qt.PenStyle.NoPen)

        """Route verticale et horizontale"""
        self.scene.addRect(330, 0, 140, 800, sans_bordure, route)
        self.scene.addRect(0, 330, 800, 140, sans_bordure, route)

        """MARQUAGE AU SOL"""
        stylo_ligne_discontinue = QPen(QColor("white"))
        stylo_ligne_discontinue.setWidth(4)
        stylo_ligne_discontinue.setStyle(Qt.PenStyle.DashLine)

        """Lignes verticales (Haut et Bas) - Le centre est à x=400"""
        self.scene.addLine(400, 0, 400, 330, stylo_ligne_discontinue)
        self.scene.addLine(400, 470, 400, 800, stylo_ligne_discontinue)

        """Lignes horizontales (Gauche et Droite) - Le centre est à y=400"""
        self.scene.addLine(0, 400, 330, 400, stylo_ligne_discontinue)
        self.scene.addLine(470, 400, 800, 400, stylo_ligne_discontinue)

        """LIGNES D'ARRÊT (Lignes continus aux feux) """
        stylo_ligne_arret = QPen(QColor("white"))
        stylo_ligne_arret.setWidth(6)

        """Lignes d'arrêt (Nord, Sud, Ouest, Est)"""
        self.scene.addLine(330, 330, 400, 330, stylo_ligne_arret)
        self.scene.addLine(400, 470, 470, 470, stylo_ligne_arret)
        self.scene.addLine(330, 400, 330, 470, stylo_ligne_arret)
        self.scene.addLine(470, 330, 470, 400, stylo_ligne_arret)

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

        self.etat_urgence = False
        # Timer des feux
        self.timer_feux = QTimer(self)
        self.timer_feux.timeout.connect(self.changer_feux)
        self.timer_feux.start(5000)

        self.changer_feux()



        self.panneau_urgence = QGraphicsTextItem(
            "!!! URGENCE : SERREZ A DROITE !!!"
        )

        police = QFont("Arial", 20, QFont.Weight.Bold)
        self.panneau_urgence.setFont(police)
        self.panneau_urgence.setDefaultTextColor(QColor("red"))
        self.panneau_urgence.setPos(120, 50)

        self.scene.addItem(self.panneau_urgence)
        self.panneau_urgence.hide()

        # Bouton
        self.bouton_urgence = QPushButton("Déclencher l'Urgence")
        self.bouton_urgence.clicked.connect(self.basculer_urgence)

        self.addToolBar("Urgence").addWidget(self.bouton_urgence)

        self.bouton_generer = QPushButton("Générer une voiture")
        self.bouton_generer.clicked.connect(self.generer_voiture)
        self.addToolBar("Véhicules").addWidget(self.bouton_generer)

    def recevoir_serveur(self):

        try:
            data = self.sock.recv(1024)

            if not data:
                print("Erreur de connexion")
                self.timer_serveur.stop()
                return

            message = data.decode().strip()

            # Sépare le numéro du client du message
            try:
                numero, message = message.split("|", 1)
            except:
                print("test")

            if message.startswith("Vehicule"):

                decoupage = message.split(",")

                x = int(decoupage[0].split()[1])
                y = int(decoupage[1])
                direction = decoupage[2].strip()

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

            elif message.startswith("Urgence"):
                print("Véhicule d'urgence connecté ")
                decoupage = message.split(",")

                x = int(decoupage[0].split()[1])
                y = int(decoupage[1])
                direction = decoupage[2].strip()

                if numero not in self.voitures:
                    self.voitures[numero] = self.scene.addRect(
                        0,
                        0,
                        20,
                        20,
                        QPen(Qt.PenStyle.NoPen),
                        QBrush(QColor("red"))
                    )
                # Déplacer la voiture
                self.voitures[numero].setPos(x, y)

            elif message.startswith("deco"):
                if numero in self.voitures:
                    voiture = self.voitures.pop(numero)
                    self.scene.removeItem(voiture)
        except BlockingIOError:
            pass


    def changer_feux(self):

        if self.etat_urgence:
            pinceau_rouge = QBrush(QColor("red"))
            for feu in self.feux:
                feu.setBrush(pinceau_rouge)
            """Comme 99(on l'envoie au serveur) tous les véhicules civils vont s'arrêter !"""
            self.sock.sendall(b"phase-feu,99\n")
            return

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

        """Les deux premiers feux sont verticaux"""
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

        self.etat_urgence = not self.etat_urgence

        if self.etat_urgence:
            self.panneau_urgence.show()
            self.bouton_urgence.setText("Fin de l'urgence")

            self.sock.sendall(b"Urgence,On\n")

            self.changer_feux()

            nouvelle_ambulance = Ambulance(direction="bas")
            thread_ambu = threading.Thread(target=nouvelle_ambulance.run, daemon=True)
            thread_ambu.start()

        else:
            self.panneau_urgence.hide()
            self.bouton_urgence.setText("Déclencher l'Urgence")

            self.sock.sendall(b"Urgence,OFF\n")

            self.changer_feux()

    def generer_voiture(self):
        directions_possibles = ["bas", "haut", "gauche", "droite"]
        direction_aleatoire = random.choice(directions_possibles)
        nouvelle_voiture = Vehicule(direction=direction_aleatoire)
        thread_voiture = threading.Thread(target=nouvelle_voiture.run, daemon=True)
        thread_voiture.start()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetreCarrefour()
    fenetre.show()

    sys.exit(app.exec())