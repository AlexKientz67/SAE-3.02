import sys
import socket
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QPushButton
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QTimer
from car import Vehicule


class FenetreCarrefour(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maquette de carrefour")
        self.setGeometry(100, 100, 800, 800)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 800)

        self.vue = QGraphicsView(self.scene)
        self.setCentralWidget(self.vue)

        self.scene.setBackgroundBrush(QBrush(QColor("lightgray")))

        route = QBrush(QColor(50, 50, 50))
        sans_bordure = QPen(Qt.PenStyle.NoPen)

        self.scene.addRect(330, 0, 140, 800, sans_bordure, route)
        self.scene.addRect(0, 330, 800, 140, sans_bordure, route)

        self.feu_haut = self.scene.addEllipse(
            340, 290, 20, 20, sans_bordure, QBrush(QColor("red"))
        )
        self.feu_bas = self.scene.addEllipse(
            440, 480, 20, 20, sans_bordure, QBrush(QColor("red"))
        )
        self.feu_gauche = self.scene.addEllipse(
            310, 440, 20, 20, sans_bordure, QBrush(QColor("red"))
        )
        self.feu_droite = self.scene.addEllipse(
            480, 340, 20, 20, sans_bordure, QBrush(QColor("red"))
        )

        self.phase_feu = 0

        self.timer_feux = QTimer(self)
        self.timer_feux.timeout.connect(self.changer_feux)
        self.timer_feux.start(2000)

        self.changer_feux()

        self.voitures = {}
        self.vehicules = []

        self.bouton_generer = QPushButton("Générer une voiture")
        self.bouton_generer.clicked.connect(self.generer_voiture)
        self.addToolBar("Véhicules").addWidget(self.bouton_generer)

        self.connexion = socket.create_connection(("127.0.0.1", 6000))
        self.connexion.sendall(b"carrefour\n")
        self.connexion.setblocking(False)

        self.timer_reseau = QTimer(self)
        self.timer_reseau.timeout.connect(self.recevoir_positions)
        self.timer_reseau.start(20)

    def changer_feux(self):
        rouge = QBrush(QColor("red"))
        orange = QBrush(QColor("orange"))
        vert = QBrush(QColor("green"))

        if self.phase_feu == 0:
            self.feu_haut.setBrush(vert)
            self.feu_bas.setBrush(vert)
            self.feu_gauche.setBrush(rouge)
            self.feu_droite.setBrush(rouge)

        elif self.phase_feu == 1:
            self.feu_haut.setBrush(orange)
            self.feu_bas.setBrush(orange)

        elif self.phase_feu == 2:
            self.feu_haut.setBrush(rouge)
            self.feu_bas.setBrush(rouge)
            self.feu_gauche.setBrush(vert)
            self.feu_droite.setBrush(vert)

        elif self.phase_feu == 3:
            self.feu_gauche.setBrush(orange)
            self.feu_droite.setBrush(orange)

        self.phase_feu = (self.phase_feu + 1) % 4

    def generer_voiture(self):
        self.vehicules = [v for v in self.vehicules if v.is_alive()]

        positions = [v.y for v in self.vehicules]
        positions += [v.y() for v in self.voitures.values()]

        y = int(min([60] + positions)) - 60

        voiture = Vehicule(340, y)
        self.vehicules.append(voiture)
        voiture.start()

    def recevoir_positions(self):
        try:
            message = self.connexion.recv(4096).decode().strip()
        except:
            return

        if not message:
            self.timer_reseau.stop()
            self.connexion.close()

            for voiture in self.vehicules:
                voiture.arreter()

            for identifiant in list(self.voitures):
                self.retirer_voiture(identifiant)

            self.setWindowTitle("Carrefour déconnecté")
            return

        type, identifiant, x, y = message.split(",")

        if type == "position":
            self.mettre_a_jour_voiture(
                int(identifiant),
                int(x),
                int(y)
            )

    def mettre_a_jour_voiture(self, identifiant, x, y):
        if identifiant not in self.voitures:
            couleurs = ["blue", "yellow", "cyan", "magenta"]

            self.voitures[identifiant] = self.scene.addRect(
                0, 0, 20, 40,
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