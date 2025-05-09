import mysql.connector

def create_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='Saksham', 
        password='Saksham',
        database='StarlightHotel'
    )
    return connection
