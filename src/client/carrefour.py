import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import Qt
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
        self.setGeometry(x, y, 800, 800)

        """ La 'Scene' contient toutes les données (le fond, les routes, les voitures)"""
        self.scene = QGraphicsScene()
        """On fixe la taille de la Scène 800 * 800"""
        self.scene.setSceneRect(0, 0, 800, 800)
        """Camera qui affiche la scène dans la fenêtre"""
        self.vue = QGraphicsView(self.scene, self)
        """On définit la vue comme élément centrale de la fenêtre"""
        self.setCentralWidget(self.vue)
        self.scene.setBackgroundBrush(QBrush(QColor("lightgray")))

if __name__ == '__main__':
    """l'instance de l'application (le moteur PyQt)"""
    app = QApplication(sys.argv)

    """Instancie la classe"""
    fenetre = FenetreCarrefour()

    fenetre.show()
    """Lance la boucle d'exécution (pour que la fenêtre reste ouverte"""
    sys.exit(app.exec())
