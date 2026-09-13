"""Serveur sans interface graphique ; affichage dans client/carrefour.py."""
from traffic import SimulationServeur


HOST = "127.0.0.1"
PORT = 6000


class Server(SimulationServeur):
    def __init__(self):
        super().__init__(HOST, PORT)
        print(f"Serveur démarré sur {HOST}:{PORT}", flush=True)


def main():
    server = Server()
    try:
        # Maintient le serveur actif sans boucle graphique Qt.
        while not server.arret.wait(1):
            pass
    except KeyboardInterrupt:
        pass
    finally:
        server.fermer()


if __name__ == "__main__":
    main()
