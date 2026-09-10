import sys
import socket
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from protocol import encode_message, decode_messages

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000


class NetworkThread(QThread):
    message_received = Signal(object)
    connection_status = Signal(str)

    def __init__(self):
        super().__init__()
        self.sock = None
        self.running = True
        self.buffer = b""

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            self.sock.settimeout(0.5)

            self.sock.sendall(encode_message({
                "type": "register",
                "client": "intersection",
                "id": "CARREFOUR_1"
            }))

            self.connection_status.emit("🟢 Connecté au serveur")

            while self.running:
                try:
                    data = self.sock.recv(4096)
                    if not data:
                        break

                    self.buffer += data
                    messages, self.buffer = decode_messages(self.buffer)
                    for message in messages:
                        self.message_received.emit(message)

                except socket.timeout:
                    continue

        except OSError as exc:
            self.connection_status.emit(f"🔴 Erreur : {exc}")

        finally:
            if self.sock:
                try:
                    self.sock.close()
                except OSError:
                    pass

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        self.quit()
        self.wait(1000)


class CarrefourWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client - Carrefour 1")
        self.resize(600, 450)

        self.ns = "red"
        self.ew = "green"
        self.priority = False
        self.direction = ""

        self.status = QLabel("🟡 Connexion...")
        layout = QVBoxLayout(self)
        layout.addWidget(self.status)

        self.network = NetworkThread()
        self.network.message_received.connect(self.receive)
        self.network.connection_status.connect(self.status.setText)
        self.network.start()

    def receive(self, message):
        msg_type = message.get("type")

        if msg_type == "lights":
            self.ns = message.get("ns", self.ns)
            self.ew = message.get("ew", self.ew)
            self.priority = False
            self.update()

        elif msg_type == "priority":
            self.direction = message.get("direction", "")
            self.priority = True
            vertical = self.direction in ("NORD", "SUD")
            self.ns = "green" if vertical else "red"
            self.ew = "red" if vertical else "green"
            self.status.setText(
                f"🚑 PRIORITÉ {self.direction}"
            )
            self.update()

        elif msg_type == "resume_normal":
            self.priority = False
            self.direction = ""
            self.ns = "red"
            self.ew = "green"
            self.status.setText("🟢 Mode normal")
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, (h + 25) // 2
        road_w = 150

        p.fillRect(self.rect(), QColor("#72b957"))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#363636"))
        p.drawRect(cx - road_w // 2, 25, road_w, h)
        p.drawRect(0, cy - road_w // 2, w, road_w)

        p.setPen(QPen(Qt.white, 2))
        for y in range(35, h, 25):
            if not (cy - road_w // 2 < y < cy + road_w // 2):
                p.drawLine(cx, y, cx, min(y + 11, h))
        for x in range(0, w, 25):
            if not (cx - road_w // 2 < x < cx + road_w // 2):
                p.drawLine(x, cy, min(x + 11, w), cy)

        self.draw_light(p, cx - 110, cy - 110, self.ns)
        self.draw_light(p, cx + 68, cy - 110, self.ns)
        self.draw_light(p, cx - 110, cy + 65, self.ew)
        self.draw_light(p, cx + 68, cy + 65, self.ew)

        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(15, 45, "CARREFOUR 1")
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

        for i, name in enumerate(("red", "yellow", "green")):
            p.setBrush(colors[name] if name == active else QColor("#555555"))
            p.drawEllipse(x + 9, y + 8 + i * 31, 24, 24)

    def closeEvent(self, event):
        self.network.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarrefourWidget()
    window.show()
    sys.exit(app.exec())
