import mysql.connector

DB_CONFIG = {
    "host": "web-01.kzcloud.fr",
    "user": "carrefour",
    "password": "x*9l4IWGbaeq@hw3",
    "database": "carrefour"
}


def add_urgence(direction: str, duree: int):
    """Enregistre la direction et la durée d’une urgence avec la date et l’heure actuelles."""

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        sql = """
            INSERT INTO urgences (direction, duree, date, heure)
            VALUES (%s, %s, CURDATE(), CURTIME())
        """

        cursor.execute(sql, (direction, duree))
        connection.commit()

    except mysql.connector.Error as e:
        print("Erreur MySQL :", e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_stats():
    """Récupère le bilan des urgences, leur répartition par direction et les dix dernières interventions."""

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*), AVG(duree), MAX(duree) FROM urgences")
        resume = cursor.fetchone()

        cursor.execute("SELECT direction, COUNT(*) FROM urgences GROUP BY direction")
        par_direction = cursor.fetchall()

        cursor.execute(
            "SELECT date, heure, direction, duree FROM urgences ORDER BY id DESC LIMIT 10"
        )
        dernieres = cursor.fetchall()

        return resume, par_direction, dernieres

    except mysql.connector.Error as e:
        print("Erreur MySQL :", e)
        return (0, 0, 0), [], []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()