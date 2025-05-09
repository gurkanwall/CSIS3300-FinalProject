from db_connection import create_connection
import mysql.connector
from datetime import datetime

def view_services(connection):
    cursor = connection.cursor()
    sql = "SELECT ServiceID, ServiceType, Description, Price FROM Services"
    cursor.execute(sql)
    services = cursor.fetchall()
    
    if services:
        print("\n" + "="*60)
        print("                Available Services")
        print("="*60)
        print(f"{'Service ID':<12} | {'Service Type':<20} | {'Price':<10} | {'Description':<20}")
        print("-" * 60)
        for service in services:
            service_id, service_type, description, price = service
            print(f"{service_id:<12} | {service_type:<20} | ${price:<10.2f} | {description:<20}")
        print("="*60 + "\n")
    else:
        print("No services available.")
        
    cursor.close()

def view_room_availability(connection):
    cursor = connection.cursor()
    sql = "SELECT RoomID, RoomType, Price FROM Rooms WHERE Availability = 'Available'"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    
    if rooms:
        print("\n" + "="*50)
        print("           Available Rooms")
        print("="*50)
        print(f"{'Room Number':<10} | {'Room Type':<15} | {'Price':<10}")
        print("-" * 50)
        for room in rooms:
            room_id, room_type, price = room
            print(f"{room_id:<10} | {room_type:<15} | ${price:<10.2f}")
        print("="*50 + "\n")
        print("Press Enter to go to menu")
        input()
    else:
        print("No rooms available.")
        
    cursor.close()


def book_room(connection, user_id):
    cursor = connection.cursor()
    view_room_availability(connection)
    

    while True:
        check_in_date_str = input("Enter Check-In Date (YYYY-MM-DD): ")
        check_out_date_str = input("Enter Check-Out Date (YYYY-MM-DD): ")
        
        try:
            check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()

            if check_in_date < current_date:
                print("Check-in date cannot be before the current date. Please try again.")
                continue
            if check_out_date <= check_in_date:
                print("Check-out date must be after the check-in date. Please try again.")
                continue

            
            break
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
            continue

    room_id = input("Enter Room ID: ")

    
    num_days = (check_out_date - check_in_date).days

    
    cursor.execute("SELECT Price FROM Rooms WHERE RoomID = %s", (room_id,))
    room_price = cursor.fetchone()
    if not room_price:
        print("Invalid Room ID.")
        cursor.close()
        return
    room_price = room_price[0]

    
    total_cost = num_days * room_price

    
    sql = """
        INSERT INTO Bookings (UserID, RoomID, CheckInDate, CheckOutDate, BookingStatus, TotalCost)
        VALUES (%s, %s, %s, %s, 'Pending', %s)
    """
    values = (user_id, room_id, check_in_date, check_out_date, total_cost)

    try:
        cursor.execute(sql, values)
        connection.commit()
        print(f"Room booking request submitted. Total cost for {num_days} days is ${total_cost:.2f}.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()


def view_customer_bookings(connection, user_id):
    cursor = connection.cursor()
    sql = """
    SELECT b.BookingID, r.RoomID, b.BookingStatus, b.CheckInDate, b.CheckOutDate, b.CheckedInTime, b.CheckedOutTime, b.CreatedAt, b.TotalCost
    FROM Bookings b
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.UserID = %s
    """
    cursor.execute(sql, (user_id,))
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- Your Bookings ---")
        print(f"{'Booking ID':<12} | {'Room ID':<10} | {'Status':<12} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Checked In Time':<20} | {'Checked Out Time':<20} | {'Created At':<20} | {'Total Cost':<10}")
        print("-" * 180)
        for booking in bookings:
            booking_id, room_id, status, check_in_date, check_out_date, checked_in_time, checked_out_time, created_at, total_cost = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            checked_in_time = checked_in_time.strftime('%Y-%m-%d %H:%M:%S') if checked_in_time else 'N/A'
            checked_out_time = checked_out_time.strftime('%Y-%m-%d %H:%M:%S') if checked_out_time else 'N/A'
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'N/A'
            total_cost = f"${total_cost:.2f}" if total_cost is not None else 'N/A'
            print(f"{booking_id:<12} | {room_id:<10} | {status:<12} | {check_in_date:<15} | {check_out_date:<15} | {checked_in_time:<20} | {checked_out_time:<20} | {created_at:<20} | {total_cost:<10}")
        print("-" * 180)
    else:
        print("You have no bookings.")
    
    cursor.close()
    
def view_customer_approved_bookings(connection, user_id):
    cursor = connection.cursor()
    sql = """
    SELECT b.BookingID, r.RoomID, b.BookingStatus, b.CheckInDate, b.CheckOutDate, b.CheckedInTime, b.CheckedOutTime, b.CreatedAt, b.TotalCost
    FROM Bookings b
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.UserID = %s AND b.BookingStatus IN ('Approved', 'Checked In')
    """
    cursor.execute(sql, (user_id,))
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- Your Valid Bookings ---")
        print(f"{'Booking ID':<12} | {'Room ID':<10} | {'Status':<12} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Checked In Time':<20} | {'Checked Out Time':<20} | {'Created At':<20} | {'Total Cost':<10}")
        print("-" * 180)
        for booking in bookings:
            booking_id, room_id, status, check_in_date, check_out_date, checked_in_time, checked_out_time, created_at, total_cost = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            checked_in_time = checked_in_time.strftime('%Y-%m-%d %H:%M:%S') if checked_in_time else 'N/A'
            checked_out_time = checked_out_time.strftime('%Y-%m-%d %H:%M:%S') if checked_out_time else 'N/A'
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'N/A'
            total_cost = f"${total_cost:.2f}" if total_cost is not None else 'N/A'
            print(f"{booking_id:<12} | {room_id:<10} | {status:<12} | {check_in_date:<15} | {check_out_date:<15} | {checked_in_time:<20} | {checked_out_time:<20} | {created_at:<20} | {total_cost:<10}")
        print("-" * 180)
        return True
    else:
        return False
    
    cursor.close()


def cancel_booking(connection, user_id):
    cursor = connection.cursor()

    sql = """
    SELECT b.BookingID, r.RoomID, b.BookingStatus, b.CheckInDate, b.CheckOutDate, b.CheckedInTime, b.CheckedOutTime, b.CreatedAt, b.TotalCost
    FROM Bookings b
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.UserID = %s AND b.BookingStatus IN ('Approved', 'Pending')
    """
    cursor.execute(sql, (user_id,))
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- Your Approved or Pending Bookings ---")
        print(f"{'Booking ID':<12} | {'Room ID':<10} | {'Status':<12} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Checked In Time':<20} | {'Checked Out Time':<20} | {'Created At':<20} | {'Total Cost':<10}")
        print("-" * 180)
        for booking in bookings:
            booking_id, room_id, status, check_in_date, check_out_date, checked_in_time, checked_out_time, created_at, total_cost = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            checked_in_time = checked_in_time.strftime('%Y-%m-%d %H:%M:%S') if checked_in_time else 'N/A'
            checked_out_time = checked_out_time.strftime('%Y-%m-%d %H:%M:%S') if checked_out_time else 'N/A'
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'N/A'
            total_cost = f"${total_cost:.2f}" if total_cost is not None else 'N/A'
            print(f"{booking_id:<12} | {room_id:<10} | {status:<12} | {check_in_date:<15} | {check_out_date:<15} | {checked_in_time:<20} | {checked_out_time:<20} | {created_at:<20} | {total_cost:<10}")
        print("-" * 180)
        
        booking_id = input("Enter Booking ID to cancel: ")
        
        sql_check = """
        SELECT BookingID, RoomID FROM Bookings
        WHERE BookingID = %s AND UserID = %s AND BookingStatus IN ('Approved', 'Pending')
        """
        cursor.execute(sql_check, (booking_id, user_id))
        valid_booking = cursor.fetchone()
        
        if valid_booking:
            room_id = valid_booking[1]
            sql_cancel = "UPDATE Bookings SET BookingStatus = 'Cancelled' WHERE BookingID = %s"
            sql_update_room = "UPDATE Rooms SET Availability = 'Available' WHERE RoomID = %s AND Availability = 'Booked'"
            sql_delete_services = "DELETE FROM RoomServices WHERE BookingID = %s"
            try:
                cursor.execute(sql_cancel, (booking_id,))
                cursor.execute(sql_update_room, (room_id,))
                cursor.execute(sql_delete_services, (booking_id,))
                connection.commit()
                print("Booking cancelled and room status updated to 'Available' successfully.")
            except mysql.connector.Error as err:
                print(f"Error: {err}")
        else:
            print("Invalid Booking ID or Booking cannot be cancelled.")
    else:
        print("You have no approved or pending bookings.")
    
    cursor.close()

def view_services_for_booking(connection, booking_id):
    cursor = connection.cursor()
    sql = """
    SELECT rs.RoomServiceID, s.ServiceType, rs.Status, rs.RequestTime, rs.CompletionTime, u.Username AS CompletedBy, s.Price
    FROM RoomServices rs
    JOIN Services s ON rs.ServiceID = s.ServiceID
    LEFT JOIN Users u ON rs.CompletedByStaffID = u.UserID
    WHERE rs.BookingID = %s
    """
    cursor.execute(sql, (booking_id,))
    services = cursor.fetchall()
    
    if services:
        print("\n--- Services for Booking ID {} ---".format(booking_id))
        print(f"{'Service ID':<12} | {'Service Type':<20} | {'Status':<12} | {'Request Time':<20} | {'Completion Time':<20} | {'Completed By':<15} | {'Price':<10}")
        print("-" * 140)
        for service in services:
            service_id, service_type, status, request_time, completion_time, completed_by, price = service
            request_time = request_time.strftime('%Y-%m-%d %H:%M:%S') if request_time else 'N/A'
            completion_time = completion_time.strftime('%Y-%m-%d %H:%M:%S') if completion_time else 'N/A'
            completed_by = completed_by if completed_by else 'N/A'
            print(f"{service_id:<12} | {service_type:<20} | {status:<12} | {request_time:<20} | {completion_time:<20} | {completed_by:<15} | ${price:<10.2f}")
        print("-" * 140)
    else:
        print("No services found for this booking.")
    
    cursor.close()




def request_room_service(connection, user_id):
    cursor = connection.cursor()
    has_approved_bookings = view_customer_approved_bookings(connection, user_id)
    
    if not has_approved_bookings:
        print("You have no approved bookings to request room service.")
        cursor.close()
        return

    booking_id = input("Enter Booking ID to request room service: ")
    view_services(connection)
    service_id = input("Enter Service ID: ")
    
    sql = """
        INSERT INTO RoomServices (BookingID, ServiceID, Status)
        VALUES (%s, %s, 'Requested')
    """
    values = (booking_id, service_id)

    try:
        cursor.execute(sql, values)
        connection.commit()
        print("Room service requested successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()


def customer_menu(connection, user_id):
    while True:
        print("\n--- Customer Menu ---")
        print("1. View Available Rooms")
        print("2. Book Room")
        print("3. Request Room Service")
        print("4. View My Bookings")
        print("5. Cancel Booking")
        print("6. View Services for Booking")
        print("7. Sign Out / Switch User")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_room_availability(connection)
        elif choice == '2':
            book_room(connection, user_id)
        elif choice == '3':
            request_room_service(connection, user_id)
        elif choice == '4':
            view_customer_bookings(connection, user_id)
        elif choice == '5':
            cancel_booking(connection, user_id)
        elif choice == '6':
            if view_customer_approved_bookings(connection, user_id):
                booking_id = input("Enter Booking ID to view services: ")
                view_services_for_booking(connection, booking_id)
        elif choice == '7':
            print("Signing out...")
            return 'signout'
        elif choice == '8':
            print("Exiting...")
            return 'exit'
        else:
            print("Invalid choice. Please try again.")
