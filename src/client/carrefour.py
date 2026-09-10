import socket

HOST = "127.0.0.1"
PORT = 6000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

print("Connecté au serveur")

client.send("Bonjour serveur, je suis le carrefour !".encode("utf-8"))

client.close()