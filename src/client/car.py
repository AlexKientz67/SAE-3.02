import time
from PyQt6.QtCore import QThread, pyqtSignal


class Vehicule(QThread):
    """ Création de la "Radio" (Signal) qui va émettre deux nombres entiers (les coordonnées X et Y)"""
    position_changee = pyqtSignal(int, int)

    def __init__(self, x_depart, y_depart):
        super().__init__()
        """ On enregistre les coordonnées de départ"""

        self.x = x_depart
        self.y = y_depart
        self.vitesse = 3
        """ La voiture avancera de 5 pixels à chaque "pas"""
        self.en_route = True

    def run(self):
        """C'est le moteur du Thread. Tant qu'il tourne, la voiture avance."""

        while self.en_route:

            self.y += self.vitesse
            self.position_changee.emit(self.x, self.y)

            time.sleep(0.05)