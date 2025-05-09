from db_connection import create_connection
import mysql.connector
import getpass
from datetime import datetime, timedelta

def add_user(connection):
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
        print("User added successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

def update_user(connection):
    cursor = connection.cursor()
    username = input("Enter the Username of the user to update: ")

    cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        print("User not found.")
        return

    while True:
        print("\nWhat do you want to update?")
        print("1. Username")
        print("2. Password")
        print("3. Role")
        print("4. First Name")
        print("5. Last Name")
        print("6. Email")
        print("7. Phone")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            new_value = input("Enter new Username: ")
            field = 'Username'
        elif choice == '2':
            new_value = getpass.getpass("Enter new Password: ")
            field = 'Password'
        elif choice == '3':
            new_value = input("Enter new Role (Admin, Manager, Staff, Customer): ")
            field = 'Role'
        elif choice == '4':
            new_value = input("Enter new First Name: ")
            field = 'FirstName'
        elif choice == '5':
            new_value = input("Enter new Last Name: ")
            field = 'LastName'
        elif choice == '6':
            new_value = input("Enter new Email: ")
            field = 'Email'
        elif choice == '7':
            new_value = input("Enter new Phone: ")
            field = 'Phone'
        elif choice == '8':
            print("Exiting update menu.")
            break
        else:
            print("Invalid choice. Please try again.")
            continue

        sql = f"UPDATE Users SET {field} = %s WHERE Username = %s"
        values = (new_value, username)

        try:
            cursor.execute(sql, values)
            connection.commit()
            print(f"{field} updated successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    cursor.close()

def view_all_users(connection):
    cursor = connection.cursor()
    sql = "SELECT UserID, Username, Role, FirstName, LastName, Email, Phone FROM Users"
    cursor.execute(sql)
    users = cursor.fetchall()
    
    if users:
        print("\n--- All Users ---")
        for user in users:
            print(f"\n\nUserID: {user[0]}, \nUsername: {user[1]}, \nRole: {user[2]}, \nFirstName: {user[3]}, \nLastName: {user[4]}, \nEmail: {user[5]}, \nPhone: {user[6]}")
        input("\nEnter to go to the Main Menu")
    else:
        print("No users found.")
        
    cursor.close()

    
def delete_user(connection):
    cursor = connection.cursor()
    view_all_users(connection);
    user_name = input("\n\nEnter Username to delete: ")

    sql = "DELETE FROM Users WHERE Username = %s"
    values = (user_name,)

    try:
        cursor.execute(sql, values)
        connection.commit()
        print("User deleted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

def view_all_bookings(connection):
    cursor = connection.cursor()
    sql = """
    SELECT b.BookingID, u.Username, r.RoomID, b.BookingStatus, b.CheckInDate, b.CheckOutDate, b.CheckedInTime, b.CheckedOutTime, b.CreatedAt
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    """
    cursor.execute(sql)
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- All Bookings ---")
        print(f"{'Booking ID':<12} | {'Username':<15} | {'Room ID':<10} | {'Status':<12} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Checked In Time':<20} | {'Checked Out Time':<20} | {'Created At':<20}")
        print("-" * 180)
        for booking in bookings:
            booking_id, username, room_id, status, check_in_date, check_out_date, checked_in_time, checked_out_time, created_at = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            checked_in_time = checked_in_time.strftime('%Y-%m-%d %H:%M:%S') if checked_in_time else 'N/A'
            checked_out_time = checked_out_time.strftime('%Y-%m-%d %H:%M:%S') if checked_out_time else 'N/A'
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'N/A'
            print(f"{booking_id:<12} | {username:<15} | {room_id:<10} | {status:<12} | {check_in_date:<15} | {check_out_date:<15} | {checked_in_time:<20} | {checked_out_time:<20} | {created_at:<20}")
        print("-" * 180)
    else:
        print("No bookings found.")
    
    cursor.close()

def view_bookings_by_first_name(connection):
    cursor = connection.cursor()
    first_name = input("Enter the first name of the person to see their bookings: ")

    sql_check_person = "SELECT UserID FROM Users WHERE FirstName = %s"
    cursor.execute(sql_check_person, (first_name,))
    user_ids = cursor.fetchall()
    
    if not user_ids:
        print(f"No person found with the first name '{first_name}'.")
        cursor.close()
        return

    user_ids = [user_id[0] for user_id in user_ids]
    format_strings = ','.join(['%s'] * len(user_ids))

    sql_view_bookings = f"""
    SELECT b.BookingID, u.Username, r.RoomID, b.BookingStatus, b.CheckInDate, b.CheckOutDate, b.CheckedInTime, b.CheckedOutTime, b.CreatedAt, b.TotalCost
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.UserID IN ({format_strings})
    """
    
    cursor.execute(sql_view_bookings, tuple(user_ids))
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- Bookings for First Name: {} ---".format(first_name))
        print(f"{'Booking ID':<12} | {'Username':<15} | {'Room ID':<10} | {'Status':<12} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Checked In Time':<20} | {'Checked Out Time':<20} | {'Created At':<20} | {'Total Cost':<10}")
        print("-" * 180)
        for booking in bookings:
            booking_id, username, room_id, status, check_in_date, check_out_date, checked_in_time, checked_out_time, created_at, total_cost = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            checked_in_time = checked_in_time.strftime('%Y-%m-%d %H:%M:%S') if checked_in_time else 'N/A'
            checked_out_time = checked_out_time.strftime('%Y-%m-%d %H:%M:%S') if checked_out_time else 'N/A'
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'N/A'
            total_cost = f"${total_cost:.2f}" if total_cost is not None else 'N/A'
            print(f"{booking_id:<12} | {username:<15} | {room_id:<10} | {status:<12} | {check_in_date:<15} | {check_out_date:<15} | {checked_in_time:<20} | {checked_out_time:<20} | {created_at:<20} | {total_cost:<10}")
        print("-" * 180)
    else:
        print(f"No bookings found for the person with the first name '{first_name}'.")

    cursor.close()

def generate_financial_reports(connection):
    cursor = connection.cursor()
    
    print("\n--- Generate Financial Reports ---")
    print("1. Daily Report")
    print("2. Monthly Report")
    print("3. Custom Date Range Report")
    choice = input("Enter your choice: ")

    if choice == '1':
        start_date = datetime.now().date()
        end_date = start_date
    elif choice == '2':
        start_date = datetime.now().replace(day=1).date()
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif choice == '3':
        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        end_date_str = input("Enter end date (YYYY-MM-DD): ")
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please try again.")
            cursor.close()
            return
    else:
        print("Invalid choice. Please try again.")
        cursor.close()
        return

    financial_summary_query = """
    SELECT 
        COALESCE(SUM(b.TotalCost), 0) AS TotalRoomRevenue,
        COALESCE(SUM(CASE WHEN rs.Status = 'Completed' THEN s.Price ELSE 0 END), 0) AS TotalServiceRevenue
    FROM Bookings b
    LEFT JOIN RoomServices rs ON b.BookingID = rs.BookingID
    LEFT JOIN Services s ON rs.ServiceID = s.ServiceID
    WHERE (DATE(b.CreatedAt) BETWEEN %s AND %s)
    OR (DATE(rs.RequestTime) BETWEEN %s AND %s)
    OR (DATE(rs.CompletionTime) BETWEEN %s AND %s)
    """
    cursor.execute(financial_summary_query, (start_date, end_date, start_date, end_date, start_date, end_date))
    financial_summary = cursor.fetchone()
    
    total_room_revenue = financial_summary[0]
    total_service_revenue = financial_summary[1]
    total_revenue = total_room_revenue + total_service_revenue

    print("\n" + "="*50)
    print("           Financial Report")
    print("="*50)
    print(f"Report Period: {start_date} to {end_date}")
    print("-" * 50)
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Revenue from Room Bookings: ${total_room_revenue:.2f}")
    print(f"Revenue from Services: ${total_service_revenue:.2f}")
    print("="*50)
    
    print("Press Enter to go back to the main menu")
    input()
    
    cursor.close()

    
def admin_menu(connection):
    while True:
        print("\n--- Admin Menu ---")
        print("1. View All Users")
        print("2. Add User")
        print("3. Update User")
        print("4. Delete User")
        print("5. View All Bookings")
        print("6. View Bookings by First Name")
        print("7. Generate Financial Reports")
        print("8. Sign Out / Switch User")
        print("9. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_all_users(connection)
        elif choice == '2':
            add_user(connection)
        elif choice == '3':
            update_user(connection)
        elif choice == '4':
            delete_user(connection)
        elif choice == '5':
            view_all_bookings(connection)
        elif choice == '6':
            view_bookings_by_first_name(connection)
        elif choice == '7':
            generate_financial_reports(connection)
        elif choice == '8':
            print("Signing out...")
            return 'signout'
        elif choice == '9':
            print("Exiting...")
            return 'exit'
        else:
            print("Invalid choice. Please try again.")