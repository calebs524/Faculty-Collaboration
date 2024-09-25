"""
    Connects to MySQL server and prints tables in 'academicworld' database.
 """
import mysql.connector


def connect_to_mysql():

    # password = input("Enter MySQL password for root user: ")
    password = "test_root"  # User: enter your password here once

    try:
        connection = mysql.connector.connect(
            user="root",
            password=password,
            database="academicworld"
        )

        if connection.is_connected():
            # print("Connected to MySQL server")
            cursor = connection.cursor()

            # List tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # if tables:
            #     # print("we got tables")
            #     # print("Tables in 'academicworld' database:")
            #     # for table in tables:
            #     #     print(table[0])
            # else:
            #     print("No tables found in 'academicworld' database.")
            return connection

    except mysql.connector.Error as error:
        print("Error connecting to MySQL server:", error)
        return None

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            return connection
            # connection.close()
            # print("MySQL connection closed")


if __name__ == "__main__":
    connect_to_mysql()
