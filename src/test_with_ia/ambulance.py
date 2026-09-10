import sys
import socket

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
)

from protocol import encode_message, decode_messages

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000


class NetworkThread(QThread):
    message_received = Signal(object)
    status_changed = Signal(str)

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
                "client": "ambulance",
                "id": "AMBULANCE_1"
            }))

            self.status_changed.emit("🟢 Ambulance connectée")

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
            self.status_changed.emit(f"🔴 Erreur : {exc}")

    def send(self, message):
        if self.sock:
            try:
                self.sock.sendall(encode_message(message))
            except OSError:
                self.status_changed.emit("🔴 Connexion perdue")

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        self.quit()
        self.wait(1000)


class AmbulanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client - Ambulance")
        self.resize(380, 260)

        self.status = QLabel("🟡 Connexion...")
        self.direction = QComboBox()
        self.direction.addItems(["NORD", "SUD", "EST", "OUEST"])

        self.button = QPushButton("🚑 DEMANDER LA PRIORITÉ")
        self.button.clicked.connect(self.request_priority)

        self.result = QLabel("Aucune demande")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>🚑 Ambulance 1</h2>"))
        layout.addWidget(self.status)
        layout.addWidget(QLabel("Direction :"))
        layout.addWidget(self.direction)
        layout.addWidget(self.button)
        layout.addWidget(self.result)

        self.network = NetworkThread()
        self.network.status_changed.connect(self.status.setText)
        self.network.message_received.connect(self.receive)
        self.network.start()

    def request_priority(self):
        direction = self.direction.currentText()

        self.network.send({
            "type": "emergency",
            "vehicle": "AMBULANCE_1",
            "direction": direction
        })

        self.result.setText(
            f"🚨 Demande envoyée : priorité {direction}"
        )

    def receive(self, message):
        if message.get("type") == "registered":
            self.result.setText("✅ Serveur : connexion acceptée")

    def closeEvent(self, event):
        self.network.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AmbulanceWindow()
    window.show()
    sys.exit(app.exec())
