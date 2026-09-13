"""Simulation autoritaire et échanges TCP (un objet JSON par ligne)."""
import json
import random
import socket
import threading
import time


class Trajet:
    def __init__(self):
        self.x, self.y = 340, 0
        self.direction = "bas"
        self.choix = random.choice(("gauche", "droite", "tout_droit"))
        self.engagee = False

    def avancer(self, phase):
        if self.direction == "bas":
            # Le nez de la voiture (40 px) reste avant le carrefour, à y=330.
            if not self.engagee and self.y + 3 > 290:
                if phase != 0:
                    self.y = 290
                    return
                self.engagee = True
            self.y += 3
            if self.choix == "droite" and self.y >= 340:
                self.y = 340
                self.direction = "gauche"
            elif self.choix == "gauche" and self.y >= 440:
                self.y = 440
                self.direction = "droite"
        else:
            self.x += 3 if self.direction == "droite" else -3
        if self.y > 800 or self.x > 800 or self.x < -40:
            self.__init__()

    def etat(self, phase):
        return dict(x=self.x, y=self.y, direction=self.direction,
                    choix=self.choix, phase=phase)


class SimulationServeur:
    def __init__(self, host, port):
        self.debut = time.monotonic()
        self.arret = threading.Event()
        self.verrou = threading.Lock()
        self.clients = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen()
        self.socket.settimeout(0.5)
        self.thread = threading.Thread(target=self.accepter, daemon=True)
        self.thread.start()

    def phase(self):
        return int((time.monotonic() - self.debut) / 2) % 4

    def accepter(self):
        while not self.arret.is_set():
            try:
                client, _ = self.socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self.servir, args=(client,), daemon=True).start()

    def servir(self, client):
        trajet = Trajet()
        client.settimeout(1)
        try:
            with client:
                while not self.arret.is_set():
                    phase = self.phase()
                    trajet.avancer(phase)
                    etat = trajet.etat(phase)
                    with self.verrou:
                        self.clients[client] = etat
                    client.sendall((json.dumps(etat) + "\n").encode("utf-8"))
                    self.arret.wait(0.05)
        except OSError:
            pass
        finally:
            with self.verrou:
                self.clients.pop(client, None)

    def etats(self):
        with self.verrou:
            return list(self.clients.values())

    def fermer(self):
        self.arret.set()
        self.socket.close()
        self.thread.join(timeout=1)
