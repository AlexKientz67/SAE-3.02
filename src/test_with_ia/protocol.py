import json


def encode_message(message: dict) -> bytes:
    """Transforme un dictionnaire Python en message JSON terminé par \\n."""
    return (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")


def decode_messages(buffer: bytes):
    """
    Extrait tous les messages JSON complets d'un buffer TCP.
    Retourne (messages, reste_du_buffer).
    """
    messages = []

    while b"\n" in buffer:
        raw, buffer = buffer.split(b"\n", 1)
        if not raw:
            continue

        try:
            messages.append(json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            messages.append({
                "type": "error",
                "message": "Message JSON invalide"
            })

    return messages, buffer
