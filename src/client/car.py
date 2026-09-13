import json
import socket
from PyQt6.QtCore import QThread, pyqtSignal


class Vehicule(QThread):
    """ Création de la "Radio" (Signal) qui va émettre deux nombres entiers (les coordonnées X et Y)"""
    position_changee = pyqtSignal(int, int)
    etat_recu = pyqtSignal(int, str)
    erreur = pyqtSignal(str)

    def __init__(self, x_depart, y_depart):
        super().__init__()
        """ On enregistre les coordonnées de départ"""

        self.x = x_depart
        self.y = y_depart
        self.vitesse = 3
        """ La voiture avancera de 5 pixels à chaque "pas"""
        self.en_route = True

    def run(self):
        """Les positions, les feux et les virages sont calculés par le serveur."""
        try:
            with socket.create_connection(("127.0.0.1", 6000), timeout=2) as connexion:
                connexion.settimeout(0.5)
                tampon = b""
                while self.en_route:
                    try:
                        donnees = connexion.recv(4096)
                    except socket.timeout:
                        continue
                    if not donnees:
                        raise ConnectionError("Le serveur a fermé la connexion.")
                    tampon += donnees
                    while b"\n" in tampon:
                        ligne, tampon = tampon.split(b"\n", 1)
                        etat = json.loads(ligne)
                        self.x, self.y = etat["x"], etat["y"]
                        self.etat_recu.emit(etat["phase"], etat["direction"])
                        self.position_changee.emit(self.x, self.y)
        except (OSError, ValueError, KeyError) as erreur:
            if self.en_route:
                self.erreur.emit(str(erreur))


if __name__ == '__main__':
    from carrefour import main
    main()
