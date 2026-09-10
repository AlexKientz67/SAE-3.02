import sys
import socket
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout

from protocol import encode_message, decode_messages

HOST = "127.0.0.1"
PORT = 5000


class ClientHandler(QThread):
    message_received = Signal(object, object)
    disconnected = Signal(object)

    def __init__(self, sock, address):
        super().__init__()
        self.sock = sock
        self.address = address
        self.running = True

    def run(self):
        buffer = b""
        self.sock.settimeout(0.5)

        try:
            while self.running:
                try:
                    data = self.sock.recv(4096)
                    if not data:
                        break
                    buffer += data
                    messages, buffer = decode_messages(buffer)
                    for message in messages:
                        self.message_received.emit(message, self)
                except socket.timeout:
                    continue
        except OSError:
            pass
        finally:
            try:
                self.sock.close()
            except OSError:
                pass
            self.disconnected.emit(self)

    def send(self, message):
        try:
            self.sock.sendall(encode_message(message))
        except OSError:
            self.running = False

    def stop(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.quit()
        self.wait(1000)


class ServerThread(QThread):
    client_connected = Signal(object, object)
    server_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.server_socket = None

    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(10)
            self.server_socket.settimeout(0.5)

            while self.running:
                try:
                    sock, address = self.server_socket.accept()
                    self.client_connected.emit(sock, address)
                except socket.timeout:
                    continue
        except OSError as exc:
            if self.running:
                self.server_error.emit(str(exc))
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except OSError:
                    pass

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
        self.quit()
        self.wait(1000)


class IntersectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(720, 520)
        self.ns = "red"
        self.ew = "green"
        self.priority = False
        self.priority_direction = None
        self.ambulance_visible = False
        self.cars_visible = True

    def set_state(self, ns, ew):
        self.ns, self.ew = ns, ew
        self.update()

    def set_priority(self, direction):
        self.priority = True
        self.priority_direction = direction
        self.ambulance_visible = True
        self.update()

    def clear_priority(self):
        self.priority = False
        self.priority_direction = None
        self.ambulance_visible = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        road_w = 190

        p.fillRect(self.rect(), QColor("#72b957"))

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#363636"))
        p.drawRect(cx - road_w // 2, 0, road_w, h)
        p.drawRect(0, cy - road_w // 2, w, road_w)

        # Marquage central
        p.setPen(QPen(Qt.white, 3))
        for y in range(0, h, 28):
            if not (cy - road_w // 2 < y < cy + road_w // 2):
                p.drawLine(cx, y, cx, min(y + 13, h))
        for x in range(0, w, 28):
            if not (cx - road_w // 2 < x < cx + road_w // 2):
                p.drawLine(x, cy, min(x + 13, w), cy)

        # Passages piétons
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.white)
        for x in range(cx - 75, cx + 76, 15):
            p.drawRect(x, cy - road_w // 2 - 24, 9, 15)
            p.drawRect(x, cy + road_w // 2 + 9, 9, 15)
        for y in range(cy - 75, cy + 76, 15):
            p.drawRect(cx - road_w // 2 - 24, y, 15, 9)
            p.drawRect(cx + road_w // 2 + 9, y, 15, 9)

        # Feux
        self.draw_light(p, cx - 135, cy - 135, self.ns)
        self.draw_light(p, cx + 90, cy - 135, self.ns)
        self.draw_light(p, cx - 135, cy + 80, self.ew)
        self.draw_light(p, cx + 90, cy + 80, self.ew)

        # Voitures
        if self.cars_visible:
            self.draw_car(p, cx - 18, cy + 145, QColor("#2980b9"), True)
            self.draw_car(p, cx + 55, cy - 175, QColor("#e74c3c"), True)
            self.draw_car(p, cx - 245, cy + 42, QColor("#f1c40f"), False)
            self.draw_car(p, cx + 175, cy - 42, QColor("#9b59b6"), False)

        # Ambulance
        if self.ambulance_visible:
            self.draw_ambulance(p, cx - 22, cy + 55)

        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 16, QFont.Bold))
        text = "MODE PRIORITÉ" if self.priority else "MODE NORMAL"
        p.drawText(20, 30, text)

        if self.priority_direction:
            p.setFont(QFont("Arial", 12))
            p.drawText(20, 52, f"Direction ambulance : {self.priority_direction}")

        p.end()

    def draw_light(self, p, x, y, active):
        p.setPen(QPen(QColor("#222222"), 2))
        p.setBrush(QColor("#202020"))
        p.drawRoundedRect(x, y, 42, 105, 8, 8)

        colors = {
            "red": QColor("#e74c3c"),
            "yellow": QColor("#f1c40f"),
            "green": QColor("#2ecc71"),
        }
        names = ["red", "yellow", "green"]
        for i, name in enumerate(names):
            p.setBrush(colors[name] if name == active else QColor("#555555"))
            p.drawEllipse(x + 9, y + 8 + i * 31, 24, 24)

    def draw_car(self, p, x, y, color, vertical):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        if vertical:
            p.drawRoundedRect(x, y, 36, 66, 8, 8)
            p.setBrush(QColor("#b9d7e8"))
            p.drawRect(x + 7, y + 10, 22, 17)
        else:
            p.drawRoundedRect(x, y, 66, 36, 8, 8)
            p.setBrush(QColor("#b9d7e8"))
            p.drawRect(x + 10, y + 7, 17, 22)

    def draw_ambulance(self, p, x, y):
        p.setPen(QPen(Qt.black, 2))
        p.setBrush(Qt.white)
        p.drawRoundedRect(x, y, 44, 86, 8, 8)
        p.setBrush(QColor("#e74c3c"))
        p.drawRect(x + 3, y + 38, 38, 5)
        p.drawRect(x + 19, y + 21, 6, 39)
        p.setBrush(QColor("#3498db"))
        p.drawRect(x + 12, y - 8, 20, 8)


class ServerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serveur - Gestion intelligente du carrefour")
        self.resize(1100, 650)

        self.clients = {}
        self.handlers = []

        self.intersection = IntersectionWidget()
        self.status = QLabel(f"🟢 Serveur actif — {HOST}:{PORT}")

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.clients_label = QLabel("Clients connectés : 0")

        right = QVBoxLayout()
        right.addWidget(QLabel("<b>Supervision</b>"))
        right.addWidget(self.status)
        right.addWidget(self.clients_label)
        right.addWidget(self.log)

        main = QHBoxLayout()
        main.addWidget(self.intersection, 2)

        panel = QWidget()
        panel.setLayout(right)
        main.addWidget(panel, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(main)

        self.server = ServerThread()
        self.server.client_connected.connect(self.new_client)
        self.server.server_error.connect(self.server_error)
        self.server.start()

        self.normal_timer = QTimer(self)
        self.normal_timer.timeout.connect(self.normal_cycle)
        self.normal_timer.start(4000)

        self.cycle_ns = False

        self.log_msg(f"Serveur démarré sur {HOST}:{PORT}")

    def log_msg(self, text):
        self.log.append(text)

    def new_client(self, sock, address):
        handler = ClientHandler(sock, address)
        handler.message_received.connect(self.receive_message)
        handler.disconnected.connect(self.client_disconnected)

        self.handlers.append(handler)
        handler.start()

        self.log_msg(f"🟢 Connexion TCP : {address}")
        self.update_clients()

    def receive_message(self, message, handler):
        msg_type = message.get("type")

        if msg_type == "register":
            client_id = message.get("id", "inconnu")
            client_type = message.get("client", "unknown")
            self.clients[handler] = {
                "id": client_id,
                "type": client_type,
                "address": handler.address,
            }
            self.log_msg(f"📡 {client_id} enregistré ({client_type})")
            handler.send({
                "type": "registered",
                "message": "Connexion acceptée"
            })
            self.update_clients()

        elif msg_type == "emergency":
            direction = message.get("direction", "NORD").upper()
            vehicle = message.get("vehicle", "AMBULANCE")
            self.log_msg(
                f"🚑 DEMANDE PRIORITÉ : {vehicle} → direction {direction}"
            )
            self.activate_priority(direction)

        elif msg_type == "status":
            self.log_msg(
                f"ℹ️ État carrefour : {message.get('ns')} / {message.get('ew')}"
            )

        elif msg_type == "passed":
            self.log_msg("🚑 Passage de l'ambulance terminé")
            self.finish_priority()

        elif msg_type == "error":
            self.log_msg(f"❌ {message.get('message')}")

    def activate_priority(self, direction):
        self.normal_timer.stop()
        self.intersection.set_priority(direction)

        # Axe prioritaire : vertical pour NORD/SUD, horizontal pour EST/OUEST.
        vertical = direction in ("NORD", "SUD")
        ns = "green" if vertical else "red"
        ew = "red" if vertical else "green"

        # Dans la maquette, on passe directement à l'état prioritaire.
        # Le carrefour client reçoit la même commande.
        self.set_intersection_state(ns, ew)

        for handler, info in self.clients.items():
            if info["type"] == "intersection":
                handler.send({
                    "type": "priority",
                    "direction": direction,
                    "duration": 8
                })

        self.log_msg(f"🚦 PRIORITÉ activée pour {direction}")

    def finish_priority(self):
        self.intersection.clear_priority()
        self.set_intersection_state("red", "green")

        for handler, info in self.clients.items():
            if info["type"] == "intersection":
                handler.send({"type": "resume_normal"})

        self.log_msg("🔄 Retour au fonctionnement normal")
        self.normal_timer.start(4000)

    def set_intersection_state(self, ns, ew):
        self.intersection.set_state(ns, ew)
        for handler, info in self.clients.items():
            if info["type"] == "intersection":
                handler.send({
                    "type": "lights",
                    "ns": ns,
                    "ew": ew
                })

    def normal_cycle(self):
        if self.intersection.priority:
            return

        self.cycle_ns = not self.cycle_ns
        if self.cycle_ns:
            self.set_intersection_state("green", "red")
        else:
            self.set_intersection_state("red", "green")

    def client_disconnected(self, handler):
        info = self.clients.pop(handler, None)
        if info:
            self.log_msg(f"🔴 Déconnexion : {info['id']}")
        else:
            self.log_msg(f"🔴 Déconnexion : {handler.address}")

        if handler in self.handlers:
            self.handlers.remove(handler)

        self.update_clients()

    def update_clients(self):
        self.clients_label.setText(
            f"Clients connectés : {len(self.clients)}"
        )

    def server_error(self, error):
        self.status.setText(f"🔴 Erreur serveur : {error}")
        self.log_msg(f"❌ {error}")

    def closeEvent(self, event):
        self.server.stop()
        for handler in list(self.handlers):
            handler.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
