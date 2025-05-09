from db_connection import create_connection
from admin_methods import admin_menu
from manager_methods import manager_menu
from staff_methods import staff_menu
from customer_methods import customer_menu
import getpass

def register_user(connection):
    cursor = connection.cursor()
    username = input("Enter Username: ")
    password = getpass.getpass("Enter Password: ") 
    role = input("Enter Role (Admin, Manager, Staff, Customer): ")
    first_name = input("Enter First Name: ")
    last_name = input("Enter Last Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")

    sql = """
        INSERT INTO Users (Username, Password, Role, FirstName, LastName, Email, Phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (username, password, role, first_name, last_name, email, phone)

    try:
        cursor.execute(sql, values)
        connection.commit()
        print("User registered successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

def login_user(connection):
    cursor = connection.cursor()
    username = input("Enter Username: ")
    password = getpass.getpass("Enter Password: ")

    sql = "SELECT * FROM Users WHERE Username = %s AND Password = %s"
    values = (username, password)

    cursor.execute(sql, values)
    user = cursor.fetchone()
    cursor.close()

    if user:
        print(f"Login successful. Welcome, {user[4]} {user[5]} ({user[3]}).") 
        return user
    else:
        print("Invalid username or password.")
        return None

def main():
    connection = create_connection()
    if connection and connection.is_connected():
        while True:
            user = None
            while not user:
                user = login_user(connection)
                if not user:
                    print("Login failed. Please try again.")
            user_id = user[0]  
            role = user[3]
            action = None
            if role == 'Admin':
                action = admin_menu(connection)
            elif role == 'Manager':
                action = manager_menu(connection)
            elif role == 'Staff':
                action = staff_menu(connection, user_id)
            elif role == 'Customer':
                action = customer_menu(connection, user_id)
            
            if action == 'exit':
                break
            elif action == 'signout':
                continue 
        connection.close()
    else:
        print("Failed to connect to the database.")

if __name__ == '__main__':
    main()
