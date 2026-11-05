import sys
import socket
import threading
import random
import carrefour_db

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
    QPushButton,
    QGraphicsTextItem
)

from PyQt6.QtGui import (
    QColor,
    QBrush,
    QPen,
    QFont
)

from PyQt6.QtCore import (
    Qt,
    QTimer,
    QUrl
)

from PyQt6.QtMultimedia import QSoundEffect

from client import Vehicule
from client_urgence import Vehicule_Urgence as Ambulance


class FenetreCarrefour(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE 3.02 - ProxmoxVE")
        self.setGeometry(100, 100, 800, 800)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 800)

        self.vue = QGraphicsView(self.scene)
        self.setCentralWidget(self.vue)

        self.scene.setBackgroundBrush(
            QBrush(QColor("#4CAF50"))
        )

        HOST = "127.0.0.1"
        PORT = 6000

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.sock.connect((HOST, PORT))

        # Identification du client
        self.sock.sendall(b"carrefour\n")

        # On garde le TCP non bloquant
        self.sock.setblocking(False)

        print("Connecté au serveur")

        self.voitures = {}

        route = QBrush(QColor(50, 50, 50))
        sans_bordure = QPen(Qt.PenStyle.NoPen)

        # Route verticale
        self.scene.addRect(
            330, 0, 140, 800,
            sans_bordure,
            route
        )

        # Route horizontale
        self.scene.addRect(
            0, 330, 800, 140,
            sans_bordure,
            route
        )

        stylo_ligne_discontinue = QPen(QColor("white"))
        stylo_ligne_discontinue.setWidth(4)
        stylo_ligne_discontinue.setStyle(
            Qt.PenStyle.DashLine
        )

        # Vertical
        self.scene.addLine(
            400, 0,
            400, 330,
            stylo_ligne_discontinue
        )

        self.scene.addLine(
            400, 470,
            400, 800,
            stylo_ligne_discontinue
        )

        # Horizontal
        self.scene.addLine(
            0, 400,
            330, 400,
            stylo_ligne_discontinue
        )

        self.scene.addLine(
            470, 400,
            800, 400,
            stylo_ligne_discontinue
        )

        stylo_ligne_arret = QPen(QColor("white"))
        stylo_ligne_arret.setWidth(6)

        self.scene.addLine(
            330, 330,
            400, 330,
            stylo_ligne_arret
        )

        self.scene.addLine(
            400, 470,
            470, 470,
            stylo_ligne_arret
        )

        self.scene.addLine(
            330, 400,
            330, 470,
            stylo_ligne_arret
        )

        self.scene.addLine(
            470, 330,
            470, 400,
            stylo_ligne_arret
        )

        self.feux = []

        positions_feux = [
            (340, 290),
            (440, 480),
            (310, 440),
            (480, 340)
        ]

        for x, y in positions_feux:

            feu = self.scene.addEllipse(
                x,
                y,
                20,
                20,
                sans_bordure,
                QBrush(QColor("red"))
            )

            self.feux.append(feu)

        self.phase_feu = 0

        self.etat_urgence = False

        self.timer_serveur = QTimer(self)

        self.timer_serveur.timeout.connect(
            self.recevoir_serveur
        )

        self.timer_serveur.start(30)

        self.timer_feux = QTimer(self)

        self.timer_feux.timeout.connect(
            self.changer_feux
        )

        self.timer_feux.start(5000)

        self.changer_feux()

        self.panneau_urgence = QGraphicsTextItem(
            "!!! URGENCE : SERREZ A DROITE !!!"
        )

        police = QFont(
            "Arial",
            15,
            QFont.Weight.Bold
        )

        self.panneau_urgence.setFont(police)
        self.panneau_urgence.setDefaultTextColor(
            QColor("red")
        )

        self.panneau_urgence.setPos(
            15,
            50
        )

        self.scene.addItem(
            self.panneau_urgence
        )

        self.panneau_urgence.hide()

        self.bouton_urgence = QPushButton(
            "Déclencher l'Urgence"
        )

        self.bouton_urgence.clicked.connect(
            self.basculer_urgence
        )

        self.addToolBar(
            "Urgence"
        ).addWidget(
            self.bouton_urgence
        )

        self.bouton_generer = QPushButton(
            "Générer une voiture"
        )

        self.bouton_generer.clicked.connect(
            self.generer_voiture
        )

        self.addToolBar(
            "Véhicules"
        ).addWidget(
            self.bouton_generer
        )

        self.sirene = QSoundEffect()

        self.sirene.setSource(
            QUrl.fromLocalFile("sirene.wav")
        )

        self.sirene.setVolume(0)
        self.sirene.setLoopCount(-2)

    # RÉCEPTION TCP
    def recevoir_serveur(self):

        while True:

            try:
                data = self.sock.recv(4096)

                if not data:
                    print("Erreur de connexion")
                    self.timer_serveur.stop()
                    return

                messages = data.decode().splitlines()

                for message_complet in messages:

                    if not message_complet:
                        continue


                    if "|" not in message_complet:
                        continue

                    numero, message = message_complet.split(
                        "|",
                        1
                    )

                    if message.startswith("Vehicule"):

                        decoupage = message.split(",")

                        if len(decoupage) < 3:
                            continue

                        try:
                            x = int(
                                decoupage[0].split()[1]
                            )

                            y = int(
                                decoupage[1]
                            )

                        except ValueError:
                            continue

                        if numero not in self.voitures:

                            self.voitures[numero] = (
                                self.scene.addRect(
                                    0,
                                    0,
                                    20,
                                    20,
                                    QPen(
                                        Qt.PenStyle.NoPen
                                    ),
                                    QBrush(
                                        QColor("blue")
                                    )
                                )
                            )

                        # Déplacement
                        self.voitures[numero].setPos(
                            x,
                            y
                        )

                    elif message.startswith("Urgence"):

                        decoupage = message.split(",")

                        if len(decoupage) < 3:
                            continue

                        try:
                            x = int(
                                decoupage[0].split()[1]
                            )

                            y = int(
                                decoupage[1]
                            )

                        except ValueError:
                            continue

                        # Création uniquement si nécessaire
                        if numero not in self.voitures:

                            self.voitures[numero] = (
                                self.scene.addRect(
                                    0,
                                    0,
                                    20,
                                    20,
                                    QPen(
                                        Qt.PenStyle.NoPen
                                    ),
                                    QBrush(
                                        QColor("red")
                                    )
                                )
                            )

                        self.voitures[numero].setPos(
                            x,
                            y
                        )

                    elif message.startswith("deco"):

                        voiture = self.voitures.pop(
                            numero,
                            None
                        )

                        if voiture is not None:
                            self.scene.removeItem(
                                voiture
                            )

            except BlockingIOError:
                break

            except ConnectionResetError:
                print("Connexion TCP fermée")
                self.timer_serveur.stop()
                return

            except Exception as e:
                print(
                    "Erreur réception serveur :",
                    e
                )
                break

    def changer_feux(self):
        if self.etat_urgence:

            pinceau_rouge = QBrush(
                QColor("red")
            )

            for feu in self.feux:
                feu.setBrush(
                    pinceau_rouge
                )

            self.sock.sendall(
                b"phase-feu,99\n"
            )

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

        couleurs = [
            vertical,
            vertical,
            horizontal,
            horizontal
        ]

        for feu, couleur in zip(
            self.feux,
            couleurs
        ):

            if couleur == "vert":
                feu.setBrush(
                    QBrush(QColor("green"))
                )

            elif couleur == "orange":
                feu.setBrush(
                    QBrush(QColor("orange"))
                )

            else:
                feu.setBrush(
                    QBrush(QColor("red"))
                )

        self.phase_feu = (
            self.phase_feu + 1
        ) % 4

        self.sock.sendall(
            f"phase-feu,{self.phase_feu}\n".encode()
        )

    def basculer_urgence(self):

        self.etat_urgence = not self.etat_urgence

        if self.etat_urgence:

            self.panneau_urgence.show()

            self.bouton_urgence.setText(
                "Fin de l'urgence"
            )

            self.sock.sendall(
                b"Urgence,On\n"
            )

            self.changer_feux()

            self.sirene.play()

            # Création ambulance
            nouvelle_ambulance = Ambulance(
                direction="bas"
            )

            thread_ambu = threading.Thread(
                target=nouvelle_ambulance.run,
                daemon=True
            )

            thread_ambu.start()

        else:

            self.panneau_urgence.hide()

            self.bouton_urgence.setText(
                "Déclencher l'Urgence"
            )

            self.sock.sendall(
                b"Urgence,OFF\n"
            )

            self.changer_feux()

            self.sirene.stop()

    def generer_voiture(self):

        directions_possibles = [
            "bas",
            "haut",
            "gauche",
            "droite"
        ]

        direction_aleatoire = random.choice(
            directions_possibles
        )

        nouvelle_voiture = Vehicule(
            direction=direction_aleatoire
        )

        thread_voiture = threading.Thread(
            target=nouvelle_voiture.run,
            daemon=True
        )

        thread_voiture.start()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetreCarrefour()
    fenetre.show()

    sys.exit(app.exec())