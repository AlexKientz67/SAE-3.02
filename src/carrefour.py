import sys
import socket
import threading
import random
import carrefour_db
import time

HOST = "127.0.0.1"
PORT = 6000

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
    QPushButton,
    QGraphicsTextItem,
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem
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

class FenetreStats(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Statistiques des urgences")
        self.resize(480, 380)

        resume, par_direction, dernieres = carrefour_db.get_stats()
        nombre, moyenne, maxi = resume

        disposition = QVBoxLayout()

        disposition.addWidget(QLabel(f"Nombre total d'urgences : {nombre}"))
        disposition.addWidget(QLabel(f"Durée moyenne : {float(moyenne or 0):.1f} s"))
        disposition.addWidget(QLabel(f"Durée la plus longue : {maxi or 0} s"))

        texte = " | ".join(f"{d} : {n}" for d, n in par_direction)
        disposition.addWidget(QLabel(f"Par direction : {texte}"))

        tableau = QTableWidget(len(dernieres), 4)
        tableau.setHorizontalHeaderLabels(["Date", "Heure", "Direction", "Durée (s)"])

        for i, ligne in enumerate(dernieres):
            for j, valeur in enumerate(ligne):
                tableau.setItem(i, j, QTableWidgetItem(str(valeur)))

        disposition.addWidget(QLabel("10 dernières urgences :"))
        disposition.addWidget(tableau)

        self.setLayout(disposition)
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

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.sock.connect((HOST, PORT))

        # Identification du client
        self.sock.sendall(b"carrefour\n")

        # On garde le TCP non bloquant
        self.sock.setblocking(False)

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
            (296, 276),  # 0 - voie qui descend (nord)
            (486, 476),  # 1 - voie qui monte   (sud)
            (296, 476),  # 2 - voie qui va à droite (ouest)
            (486, 276),  # 3 - voie qui va à gauche (est)
        ]

        for x, y in positions_feux:


            self.scene.addRect(
                x, y, 18, 48,
                sans_bordure,
                QBrush(QColor(30, 30, 30))
            )


            lampes = {}
            for i, couleur in enumerate(["rouge", "orange", "vert"]):
                lampes[couleur] = self.scene.addEllipse(
                    x + 3, y + 3 + i * 15, 12, 12,
                    sans_bordure,
                    QBrush(QColor(60, 60, 60))
                )

            self.feux.append(lampes)

        self.phase_feu = 0

        self.etat_urgence = False
        self.phase_evacuation = False
        self.direction_ambu = "bas"
        self.debut_urgence = None

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
            "!!! VEHICULE D’URGENCE EN CIRCULATION !!!"
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
        self.chrono = QGraphicsTextItem("")
        self.chrono.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.chrono.setDefaultTextColor(QColor("white"))
        self.chrono.setPos(15, 15)
        self.scene.addItem(self.chrono)
        self.chrono.hide()

        self.timer_chrono = QTimer(self)
        self.timer_chrono.timeout.connect(self.maj_chrono)

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
        self.bouton_stats = QPushButton("Statistiques")
        self.bouton_stats.clicked.connect(self.ouvrir_stats)
        self.addToolBar("Stats").addWidget(self.bouton_stats)
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
                self.timer_serveur.stop()
                return

            except Exception as e:
                print(
                    "Erreur réception serveur :",
                    e
                )
                break
    def allumer(self, lampes, couleur):

        teintes = {
            "rouge": "red",
            "orange": "orange",
            "vert": "lime"
        }

        for nom, lampe in lampes.items():
            if nom == couleur:
                lampe.setBrush(QBrush(QColor(teintes[nom])))
            else:
                lampe.setBrush(QBrush(QColor(60, 60, 60)))

    def changer_feux(self):
        if self.etat_urgence and self.phase_evacuation:
            # Dégagement du carrefour : tous les feux au vert.
            for lampes in self.feux:
                self.allumer(lampes, "vert")
            self.sock.sendall(b"phase-feu,98\n")
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

            for lampes, couleur in zip(self.feux, couleurs):
                self.allumer(lampes, couleur)

        self.phase_feu = (
            self.phase_feu + 1
        ) % 4

        self.sock.sendall(
            f"phase-feu,{self.phase_feu}\n".encode()
        )

    def basculer_urgence(self):

        self.etat_urgence = not self.etat_urgence

        if self.etat_urgence:

            self.direction_ambu = random.choice(["bas", "haut", "gauche", "droite"])
            self.debut_urgence = time.time()

            self.panneau_urgence.setPlainText("!!! URGENCE : DEGAGEZ LE CARREFOUR !!!")
            self.panneau_urgence.show()

            self.chrono.show()
            self.timer_chrono.start(200)

            self.bouton_urgence.setText("Fin de l'urgence")
            self.sirene.play()

            # Phase de dégagement pendant 4 secondes.
            self.phase_evacuation = True
            self.changer_feux()

            QTimer.singleShot(4000, self.lancer_ambulance)

        else:

            duree = 0
            if self.debut_urgence is not None:
                duree = int(time.time() - self.debut_urgence)

            carrefour_db.add_urgence(self.direction_ambu, duree)

            self.timer_chrono.stop()
            self.chrono.hide()
            self.panneau_urgence.hide()
            self.phase_evacuation = False
            self.changer_feux()

            self.bouton_urgence.setText("Déclencher l'Urgence")
            self.sirene.stop()
    def ouvrir_stats(self):
        self.fenetre_stats = FenetreStats()
        self.fenetre_stats.show()
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

    def lancer_ambulance(self):

        if not self.etat_urgence:
            return

        self.phase_evacuation = False
        self.changer_feux()

        self.panneau_urgence.setPlainText("!!! VEHICULE D’URGENCE EN CIRCULATION !!!")

        ambulance = Ambulance(direction=self.direction_ambu)
        threading.Thread(target=ambulance.run, daemon=True).start()

    def maj_chrono(self):

        if self.debut_urgence is None:
            return

        duree = time.time() - self.debut_urgence
        self.chrono.setPlainText(f"Urgence en cours : {duree:.1f} s")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetreCarrefour()
    fenetre.show()

    sys.exit(app.exec())