import mysql.connector

DB_CONFIG = {
    "host": "web-01.kzcloud.fr",
    "user": "carrefour",
    "password": "x*9l4IWGbaeq@hw3",
    "database": "carrefour"
}


def add_urgence(direction: str):

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        sql = """
            INSERT INTO urgences (direction, date, heure)
            VALUES (%s, CURDATE(), CURTIME())
        """

        cursor.execute(sql, (direction,))
        connection.commit()
    except mysql.connector.Error as e:
        print("Erreur MySQL :", e)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def get_nombre_urgences():

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        sql = "SELECT COUNT(*) FROM urgences"

        cursor.execute(sql)
        resultat = cursor.fetchone()

        return resultat[0]

    except mysql.connector.Error as e:
        print("Erreur MySQL :", e)
        return 0

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
