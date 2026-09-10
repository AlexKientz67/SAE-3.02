import sys
import socket

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout


HOST = "127.0.0.1"
PORT = 6000


class CarrefourWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(800, 600)

        # État des feux
        self.feu_nord_sud = "rouge"
        self.feu_est_ouest = "vert"

    def paintEvent(self, event):

        painter = QPainter(self)

        # -------------------------
        # FOND
        # -------------------------

        painter.fillRect(
            self.rect(),
            QColor("#75b85a")
        )

        # -------------------------
        # ROUTES
        # -------------------------

        largeur_route = 220

        centre_x = self.width() // 2
        centre_y = self.height() // 2

        # Route verticale
        painter.setBrush(QColor("#383838"))
        painter.setPen(Qt.NoPen)

        painter.drawRect(
            centre_x - largeur_route // 2,
            0,
            largeur_route,
            self.height()
        )

        # Route horizontale
        painter.drawRect(
            0,
            centre_y - largeur_route // 2,
            self.width(),
            largeur_route
        )

        # -------------------------
        # LIGNES BLANCHES
        # -------------------------

        painter.setPen(
            QPen(Qt.white, 4)
        )

        # Ligne centrale verticale
        for y in range(0, self.height(), 30):

            if (
                centre_y - largeur_route // 2
                < y
                < centre_y + largeur_route // 2
            ):
                continue

            painter.drawLine(
                centre_x,
                y,
                centre_x,
                y + 15
            )

        # Ligne centrale horizontale
        for x in range(0, self.width(), 30):

            if (
                centre_x - largeur_route // 2
                < x
                < centre_x + largeur_route // 2
            ):
                continue

            painter.drawLine(
                x,
                centre_y,
                x + 15,
                centre_y
            )

        # -------------------------
        # PASSAGES PIÉTONS
        # -------------------------

        painter.setBrush(Qt.white)
        painter.setPen(Qt.NoPen)

        # Nord
        for x in range(
            centre_x - 90,
            centre_x + 90,
            20
        ):
            painter.drawRect(
                x,
                centre_y - largeur_route // 2 - 25,
                12,
                15
            )

        # Sud
        for x in range(
            centre_x - 90,
            centre_x + 90,
            20
        ):
            painter.drawRect(
                x,
                centre_y + largeur_route // 2 + 10,
                12,
                15
            )

        # Est
        for y in range(
            centre_y - 90,
            centre_y + 90,
            20
        ):
            painter.drawRect(
                centre_x + largeur_route // 2 + 10,
                y,
                15,
                12
            )

        # Ouest
        for y in range(
            centre_y - 90,
            centre_y + 90,
            20
        ):
            painter.drawRect(
                centre_x - largeur_route // 2 - 25,
                y,
                15,
                12
            )

        # -------------------------
        # FEUX
        # -------------------------

        self.draw_feu(
            painter,
            centre_x - 145,
            centre_y - 145,
            self.feu_nord_sud
        )

        self.draw_feu(
            painter,
            centre_x + 120,
            centre_y - 145,
            self.feu_nord_sud
        )

        self.draw_feu(
            painter,
            centre_x - 145,
            centre_y + 100,
            self.feu_est_ouest
        )

        self.draw_feu(
            painter,
            centre_x + 120,
            centre_y + 100,
            self.feu_est_ouest
        )

        # -------------------------
        # VOITURES
        # -------------------------

        self.draw_car(
            painter,
            centre_x - 25,
            centre_y + 160,
            QColor("#3498db"),
            vertical=True
        )

        self.draw_car(
            painter,
            centre_x + 70,
            centre_y - 170,
            QColor("#e74c3c"),
            vertical=True
        )

        self.draw_car(
            painter,
            centre_x - 250,
            centre_y + 40,
            QColor("#f1c40f"),
            vertical=False
        )

        self.draw_car(
            painter,
            centre_x + 180,
            centre_y - 40,
            QColor("#9b59b6"),
            vertical=False
        )

        # -------------------------
        # AMBULANCE
        # -------------------------

        self.draw_ambulance(
            painter,
            centre_x - 25,
            centre_y + 70
        )

        painter.end()

    # =====================================================
    # FEU
    # =====================================================

    def draw_feu(
        self,
        painter,
        x,
        y,
        couleur_active
    ):

        # Boîtier
        painter.setBrush(
            QColor("#222222")
        )

        painter.drawRoundedRect(
            x,
            y,
            45,
            115,
            8,
            8
        )

        couleurs = {
            "rouge": QColor("#e74c3c"),
            "jaune": QColor("#f1c40f"),
            "vert": QColor("#2ecc71")
        }

        positions = [
            ("rouge", 15),
            ("jaune", 50),
            ("vert", 85)
        ]

        for couleur, position in positions:

            if couleur == couleur_active:

                brush = QBrush(
                    couleurs[couleur]
                )

            else:

                brush = QBrush(
                    QColor("#555555")
                )

            painter.setBrush(brush)

            painter.drawEllipse(
                x + 10,
                y + position,
                25,
                25
            )

    # =====================================================
    # VOITURE
    # =====================================================

    def draw_car(
        self,
        painter,
        x,
        y,
        couleur,
        vertical=False
    ):

        painter.setBrush(couleur)
        painter.setPen(Qt.NoPen)

        if vertical:

            painter.drawRoundedRect(
                x,
                y,
                35,
                70,
                8,
                8
            )

            painter.setBrush(
                QColor("#bde3f7")
            )

            painter.drawRect(
                x + 6,
                y + 10,
                23,
                18
            )

        else:

            painter.drawRoundedRect(
                x,
                y,
                70,
                35,
                8,
                8
            )

            painter.setBrush(
                QColor("#bde3f7")
            )

            painter.drawRect(
                x + 10,
                y + 6,
                18,
                23
            )

    # =====================================================
    # AMBULANCE
    # =====================================================

    def draw_ambulance(
        self,
        painter,
        x,
        y
    ):

        # Corps
        painter.setBrush(
            Qt.white
        )

        painter.setPen(
            QPen(Qt.black, 2)
        )

        painter.drawRoundedRect(
            x,
            y,
            45,
            90,
            8,
            8
        )

        # Croix rouge
        painter.setPen(
            QPen(Qt.red, 6)
        )

        painter.drawLine(
            x + 22,
            y + 25,
            x + 22,
            y + 55
        )

        painter.drawLine(
            x + 10,
            y + 40,
            x + 34,
            y + 40
        )

        # Gyrophare
        painter.setBrush(
            QColor("#3498db")
        )

        painter.setPen(Qt.NoPen)

        painter.drawRect(
            x + 12,
            y - 8,
            20,
            8
        )


class Server:

    def __init__(self):

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.socket.bind(
            (HOST, PORT)
        )

        self.socket.listen()

        print(
            f"Serveur démarré sur "
            f"{HOST}:{PORT}"
        )


def main():

    app = QApplication(sys.argv)

    # Serveur
    server = Server()

    # Interface
    fenetre = CarrefourWidget()

    fenetre.setWindowTitle(
        "Serveur - Gestion du carrefour"
    )

    fenetre.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()