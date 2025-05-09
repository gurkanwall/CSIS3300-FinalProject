import mysql.connector 

from db_connection import create_connection 

def create_database():
    connection = mysql.connector.connect(
        host='localhost',
        user='Saksham',  
        password='Saksham'
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS StarlightHotel")
    cursor.close()
    connection.close()
    print("Database 'StarlightHotel' checked and created if not exists.")

def create_connection_with_db():
    create_database()  
    return create_connection() 
    
def check_and_create_table(connection, create_table_sql, table_name):
    if connection is not None and connection.is_connected():
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'StarlightHotel' AND TABLE_NAME = '{table_name}';")
        if cursor.fetchone()[0] == 1:
            print(f"Table '{table_name}' already exists.")
        else:
            cursor.execute(create_table_sql)
            connection.commit() 
            print(f"Table '{table_name}' created successfully.")
        cursor.close()
    else:
        print("Failed to establish a database connection.")

def create_all_tables(connection):
    if connection is not None and connection.is_connected():
        create_users_table(connection)
        create_rooms_table(connection)
        create_bookings_table(connection)
        create_services_table(connection)
        create_room_services_table(connection)
        insert_rooms_data(connection)
        insert_services_data(connection)
        insert_users_data(connection)
        connection.close()
    else:
        print("Failed to connect to the database.")

def create_users_table(connection):
    sql = """
        CREATE TABLE IF NOT EXISTS Users (
            UserID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(255) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL,
            Role ENUM('Admin', 'Manager', 'Staff', 'Customer') NOT NULL,
            FirstName VARCHAR(255),
            LastName VARCHAR(255),
            Email VARCHAR(255) UNIQUE,
            Phone VARCHAR(20)
        );
    """
    check_and_create_table(connection, sql, 'Users')

def create_rooms_table(connection):
    sql = """
        CREATE TABLE IF NOT EXISTS Rooms (
            RoomID INT AUTO_INCREMENT PRIMARY KEY,
            RoomType ENUM('Single', 'Double', 'Suite') NOT NULL,
            Availability ENUM('Available', 'Booked', 'Maintenance') NOT NULL DEFAULT 'Available',
            Price DECIMAL(10,2) NOT NULL
        );
    """
    check_and_create_table(connection, sql, 'Rooms')

def create_bookings_table(connection):
    sql = """
        CREATE TABLE IF NOT EXISTS Bookings (
            BookingID INT AUTO_INCREMENT PRIMARY KEY,
            UserID INT,
            RoomID INT,
            BookingStatus ENUM('Pending', 'Approved', 'Rejected', 'Checked In', 'Checked Out', 'Cancelled') NOT NULL DEFAULT 'Pending',
            CheckInDate DATE NOT NULL,
            CheckOutDate DATE NOT NULL,
            CheckedInTime DATETIME NULL,
            CheckedOutTime DATETIME NULL,
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            TotalCost DECIMAL(10,2) NULL,
            FOREIGN KEY (UserID) REFERENCES Users(UserID),
            FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID)
        );
    """
    check_and_create_table(connection, sql, 'Bookings')

def create_services_table(connection):
    sql = """
        CREATE TABLE IF NOT EXISTS Services (
            ServiceID INT AUTO_INCREMENT PRIMARY KEY,
            ServiceType VARCHAR(255) NOT NULL,
            Description TEXT,
            Price DECIMAL(10,2)
        );
    """
    check_and_create_table(connection, sql, 'Services')

def create_room_services_table(connection):
    sql = """
        CREATE TABLE IF NOT EXISTS RoomServices (
            RoomServiceID INT AUTO_INCREMENT PRIMARY KEY,
            BookingID INT,
            ServiceID INT,
            Status ENUM('Requested', 'Completed') NOT NULL DEFAULT 'Requested',
            RequestTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CompletionTime TIMESTAMP,
            CompletedByStaffID INT NULL,
            FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID),
            FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID),
            FOREIGN KEY (CompletedByStaffID) REFERENCES Users(UserID)
        );
    """
    check_and_create_table(connection, sql, 'RoomServices')
    
def check_table_empty(connection, table_name):
    """
    Check if a given table is empty.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count == 0
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()

def insert_rooms_data(connection):
    if check_table_empty(connection, 'Rooms'):
        sql = """
        INSERT INTO Rooms (RoomID, RoomType, Availability, Price)
        VALUES
        (101, 'Single', 'Available', 100.00),
        (102, 'Single', 'Available', 100.00),
        (103, 'Single', 'Booked', 100.00),
        (104, 'Double', 'Available', 150.00),
        (105, 'Double', 'Available', 150.00),
        (106, 'Double', 'Maintenance', 150.00),
        (201, 'Suite', 'Available', 250.00),
        (202, 'Suite', 'Available', 250.00),
        (203, 'Suite', 'Booked', 250.00),
        (204, 'Suite', 'Maintenance', 250.00),
        (301, 'Single', 'Available', 120.00),
        (302, 'Single', 'Booked', 120.00),
        (303, 'Double', 'Available', 170.00),
        (304, 'Double', 'Booked', 170.00),
        (305, 'Suite', 'Maintenance', 270.00);
        """
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            print("Rooms data inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
    else:
        print("Rooms table already contains data. Insertion skipped.")

def insert_services_data(connection):
    if check_table_empty(connection, 'Services'):
        sql = """
        INSERT INTO Services (ServiceID, ServiceType, Description, Price)
        VALUES
        (1, 'Room Cleaning', 'Daily room cleaning service', 20.00),
        (2, 'Laundry', 'Laundry service', 15.00),
        (3, 'Spa', 'Spa service', 50.00),
        (4, 'Gym', 'Access to gym facilities', 10.00),
        (5, 'Breakfast', 'Daily breakfast', 25.00),
        (6, 'Dinner', 'Daily dinner', 35.00),
        (7, 'Parking', 'Secure parking service', 10.00),
        (8, 'Internet', 'High-speed internet access', 5.00),
        (9, 'Mini Bar', 'In-room mini bar access', 30.00),
        (10, 'Pool', 'Access to swimming pool', 15.00);
        """
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            print("Services data inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
    else:
        print("Services table already contains data. Insertion skipped.")

def insert_users_data(connection):
    if check_table_empty(connection, 'Users'):
        sql = """
        INSERT INTO Users (UserID, Username, Password, Role, FirstName, LastName, Email, Phone)
        VALUES
        (1, 'admin', 'admin', 'Admin', 'Saksham', 'Vasudev', 'admin@example.com', '1234567890'),
        (2, 'manager', 'manager', 'Manager', 'Tushar', 'Bhatia', 'manager@example.com', '1234567890'),
        (3, 'staff', 'staff', 'Staff', 'Lovish', 'Dhanda', 'staff@example.com', '1234567890'),
        (4, 'customer', 'customer', 'Customer', 'Gurkanwal', 'Singh', 'customer@example.com', '1234567890');
        """
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            print("Users data inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
    else:
        print("Users table already contains data. Insertion skipped.")

if __name__ == '__main__':
    connection = create_connection_with_db() 
    create_all_tables(connection)
   
