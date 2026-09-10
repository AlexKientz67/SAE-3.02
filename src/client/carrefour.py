
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QTimer
"""
Importations des libraries importantes.
module sys = natif de python
module PyQT6 pour la partie graphique

"""
class FenetreCarrefour(QMainWindow):
    def __init__(self):

        super().__init__()

        """
        Définis le titre et la taille de la fenêtre
        """
        self.setWindowTitle("Maquette de carrefour")
        self.setGeometry(100, 100, 800, 800)

        """ La 'Scene' contient toutes les données (le fond, les routes, les voitures)"""
        self.scene = QGraphicsScene()
        """On fixe la taille de la Scène 800 * 800"""
        self.scene.setSceneRect(0, 0, 800, 800)
        """Camera qui affiche la scène dans la fenêtre"""
        self.vue = QGraphicsView(self.scene, self)
        """On définit la vue comme élément centrale de la fenêtre"""
        self.setCentralWidget(self.vue)
        self.scene.setBackgroundBrush(QBrush(QColor("lightgray")))

        """Crée le style de la route (bordure transparente, remplissage gris foncé)"""

        couleur_route = QColor(50, 50, 50)
        pinceau_route = QBrush(couleur_route)
        stylo_sans_bordure = QPen(Qt.PenStyle.NoPen)
        pinceau_rouge  = QColor("red")


        """ Route Verticale"""
        self.scene.addRect(330, 0, 140, 800, stylo_sans_bordure, pinceau_route)

        """ Route Horizontale """
        self.scene.addRect(0, 330, 800, 140, stylo_sans_bordure, pinceau_route)

        """test d'un début d'un feu rouge"""
        self.feu_haut = self.scene.addEllipse(340, 290, 20, 20, stylo_sans_bordure, pinceau_rouge)
        self.feu_bas = self.scene.addEllipse(440, 480, 20, 20, stylo_sans_bordure, pinceau_rouge)
        self.feu_gauche = self.scene.addEllipse(310, 440, 20, 20, stylo_sans_bordure, pinceau_rouge)
        self.feu_droite = self.scene.addEllipse(480, 340, 20, 20, stylo_sans_bordure, pinceau_rouge)

        self.phase_feu = 0

        self.timer_feux = QTimer(self)
        self.timer_feux.timeout.connect(self.changer_feux)
        self.timer_feux.start(2000)

        self.changer_feux()
        """On appelle la fonction une première fois
        manuellement pour initialiser les couleurs
        """


    """Fonction de Changement de Couleur"""
    def changer_feux(self):
        pinceau_rouge = QBrush(QColor("red"))
        pinceau_orange = QBrush(QColor("orange"))
        pinceau_vert = QBrush(QColor("green"))

        if self.phase_feu == 0:
            """ Phase 0 : L'axe Vertical passe au VERT,
            L'axe Horizontal reste au Rouge."""
            self.feu_haut.setBrush(pinceau_vert)
            self.feu_bas.setBrush(pinceau_vert)
            self.feu_gauche.setBrush(pinceau_rouge)
            self.feu_droite.setBrush(pinceau_rouge)

        elif self.phase_feu == 1:
            """ L'axe Vertical passe à l'Orange
            """
            self.feu_haut.setBrush(pinceau_orange)
            self.feu_bas.setBrush(pinceau_orange)

        elif self.phase_feu == 2:
            """L'axe Vertical passe au Rouge, L'axe Horizontal passe au Vert
            """
            self.feu_haut.setBrush(pinceau_rouge)
            self.feu_bas.setBrush(pinceau_rouge)
            self.feu_gauche.setBrush(pinceau_vert)
            self.feu_droite.setBrush(pinceau_vert)

        elif self.phase_feu == 3:
            """ L'axe Horizontal passe à l'Orange
            """
            self.feu_gauche.setBrush(pinceau_orange)
            self.feu_droite.setBrush(pinceau_orange)

            """ A la fin on passe à la phase suivante
           Modulo de 4 permet de revenir a 0 après 3
           (0,1,2,3,0,1 ...)"""
        self.phase_feu = (self.phase_feu + 1) % 4

if __name__ == '__main__':
    """l'instance de l'application (le moteur PyQt)"""
    app = QApplication(sys.argv)

    """Instancie la classe"""
    fenetre = FenetreCarrefour()

    fenetre.show()
    """Lance la boucle d'exécution (pour que la fenêtre reste ouverte"""
    sys.exit(app.exec())
