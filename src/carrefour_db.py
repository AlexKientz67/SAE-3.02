
import mysql.connector
from datetime import datetime


def add_urgence(direction: str, temps_passage: int):

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host="web-01.kzcloud.fr",
            user="carrefour",
            password="x*9l4IWGbaeq@hw3",
            database="carrefour"
        )

        cursor = connection.cursor()

        sql = """
            INSERT INTO urgences (direction, temps_passage, date)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (direction, temps_passage, datetime.now()))
        connection.commit()

        print(f"Urgence ajoutée ! ID : {cursor.lastrowid}")

    except mysql.connector.Error as error:
        print(f"Erreur MySQL : {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
