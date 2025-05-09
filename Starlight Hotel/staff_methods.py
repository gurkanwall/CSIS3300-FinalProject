from db_connection import create_connection
import mysql.connector

def view_approved_bookings(connection):
    cursor = connection.cursor()
    sql = """
    SELECT b.BookingID, u.Username, r.RoomID, b.CheckInDate, b.CheckOutDate
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingStatus = 'Approved'
    """
    cursor.execute(sql)
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- Approved Bookings ---")
        print(f"{'Booking ID':<12} | {'Username':<15} | {'Room ID':<10} | {'Check-In Date':<15} | {'Check-Out Date':<15}")
        print("-" * 80)
        for booking in bookings:
            booking_id, username, room_id, check_in_date, check_out_date = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            print(f"{booking_id:<12} | {username:<15} | {room_id:<10} | {check_in_date:<15} | {check_out_date:<15}")
        print("-" * 80)
        cursor.close()
        return True
    else:
        print("No approved bookings.")
        cursor.close()
        return False

def view_checked_in_bookings(connection):
    cursor = connection.cursor()
    sql = """
    SELECT b.BookingID, u.Username, r.RoomID, b.CheckInDate, b.CheckOutDate
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingStatus = 'Checked In'
    """
    cursor.execute(sql)
    bookings = cursor.fetchall()
    
    if bookings:
        print("\n--- Checked-In Bookings ---")
        print(f"{'Booking ID':<12} | {'Username':<15} | {'Room ID':<10} | {'Check-In Date':<15} | {'Check-Out Date':<15}")
        print("-" * 80)
        for booking in bookings:
            booking_id, username, room_id, check_in_date, check_out_date = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            print(f"{booking_id:<12} | {username:<15} | {room_id:<10} | {check_in_date:<15} | {check_out_date:<15}")
        print("-" * 80)
        cursor.close()
        return True
    else:
        print("No checked-in bookings.")
        cursor.close()
        return False


def handle_checkin(connection):
    cursor = connection.cursor()
    if view_approved_bookings(connection):
        booking_id = input("Enter Booking ID for check-in: ")
        sql = """
            UPDATE Bookings
            SET BookingStatus = 'Checked In', CheckedInTime = NOW()
            WHERE BookingID = %s
        """
        values = (booking_id,)

        try:
            cursor.execute(sql, values)
            connection.commit()
            print("Check-in successful.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
    else:
        cursor.close()


def handle_checkout(connection):
    cursor = connection.cursor()
    if view_checked_in_bookings(connection):
        booking_id = input("Enter Booking ID for check-out: ")

        
        sql_update_booking = """
            UPDATE Bookings
            SET BookingStatus = 'Checked Out', CheckedOutTime = NOW()
            WHERE BookingID = %s
        """
        
       
        sql_get_room_id = "SELECT RoomID FROM Bookings WHERE BookingID = %s"
        cursor.execute(sql_get_room_id, (booking_id,))
        room_id = cursor.fetchone()
        
        if room_id:
            room_id = room_id[0] 
            
            
            sql_update_room = "UPDATE Rooms SET Availability = 'Maintenance' WHERE RoomID = %s"
            
            try:
                
                cursor.execute(sql_update_booking, (booking_id,))
                cursor.execute(sql_update_room, (room_id,))
                connection.commit()
                print("Check-out successful and room status set to 'Maintenance'.")
            except mysql.connector.Error as err:
                print(f"Error: {err}")
        else:
            print("Invalid Booking ID.")
        cursor.close()
    else:
        cursor.close()


def view_room_service_requests(connection):
    cursor = connection.cursor()
    sql = """
    SELECT rs.RoomServiceID, rs.BookingID, rs.ServiceID, rs.Status, rs.RequestTime, s.ServiceType
    FROM RoomServices rs
    JOIN Services s ON rs.ServiceID = s.ServiceID
    WHERE rs.Status = 'Requested'
    """
    cursor.execute(sql)
    service_requests = cursor.fetchall()
    
    if service_requests:
        print("\n--- Room Service Requests ---")
        print(f"{'Room Service ID':<15} | {'Booking ID':<12} | {'Service ID':<10} | {'Service Type':<15} | {'Status':<10} | {'Request Time':<20}")
        print("-" * 100)
        for request in service_requests:
            room_service_id, booking_id, service_id, status, request_time, service_type = request
            request_time = request_time.strftime('%Y-%m-%d %H:%M:%S') if request_time else 'N/A'
            print(f"{room_service_id:<15} | {booking_id:<12} | {service_id:<10} | {service_type:<15} | {status:<10} | {request_time:<20}")
        print("-" * 100)
    else:
        print("No room service requests.")
    
    cursor.close()

def view_serviceable_rooms(connection):
    cursor = connection.cursor()
    sql = """
    SELECT RoomID, RoomType
    FROM Rooms
    WHERE Availability = 'Maintenance'
    """
    cursor.execute(sql)
    rooms = cursor.fetchall()
    
    if rooms:
        print("\n--- Serviceable Rooms (Maintenance) ---")
        print(f"{'Room ID':<10} | {'Room Type':<15}")
        print("-" * 30)
        for room in rooms:
            room_id, room_type= room
            print(f"{room_id:<10} | {room_type:<15}")
        print("-" * 30)
        input("Press Enter to return")
    else:
        print("No rooms currently in maintenance status.")
    
    cursor.close()


def provide_room_service(connection, staff_id):
    cursor = connection.cursor()
    
    sql_check_requested = """
    SELECT COUNT(*)
    FROM RoomServices
    WHERE Status = 'Requested'
    """
    cursor.execute(sql_check_requested)
    requested_count = cursor.fetchone()[0]

    if requested_count == 0:
        print("No room service requests.")
        cursor.close()
        return

    view_room_service_requests(connection)
    
    room_service_id = input("Enter Room Service ID to complete the service: ")
    sql = """
        UPDATE RoomServices
        SET Status = 'Completed', CompletionTime = CURRENT_TIMESTAMP, CompletedByStaffID = %s
        WHERE RoomServiceID = %s
    """
    values = (staff_id, room_service_id)

    try:
        cursor.execute(sql, values)
        connection.commit()
        print("Room service completed successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()


def update_room_status(connection):
    cursor = connection.cursor()
    sql_check_maintenance = """
    SELECT RoomID, RoomType
    FROM Rooms
    WHERE Availability = 'Maintenance'
    """
    cursor.execute(sql_check_maintenance)
    maintenance_rooms = cursor.fetchall()
    
    if not maintenance_rooms:
        print("There are no rooms currently in maintenance status.")
        cursor.close()
        return
    
    view_serviceable_rooms(connection)
    
    room_id = input("Enter Room ID to update status: ")
    sql_validate = "SELECT RoomID FROM Rooms WHERE RoomID = %s AND Availability = 'Maintenance'"
    cursor.execute(sql_validate, (room_id,))
    room = cursor.fetchone()
    
    if room:
        sql_update_room = "UPDATE Rooms SET Availability = 'Available' WHERE RoomID = %s"
        values = (room_id,)

        try:
            cursor.execute(sql_update_room, values)
            connection.commit()
            print("Room status updated successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
    else:
        print("Invalid Room ID or Room is not in maintenance.")
        cursor.close()

def view_completed_services(connection):
    cursor = connection.cursor()
    sql = """
    SELECT rs.RoomServiceID, rs.BookingID, rs.ServiceID, rs.Status, rs.RequestTime, rs.CompletionTime, s.ServiceType, u.Username AS CompletedBy
    FROM RoomServices rs
    JOIN Services s ON rs.ServiceID = s.ServiceID
    LEFT JOIN Users u ON rs.CompletedByStaffID = u.UserID
    WHERE rs.Status = 'Completed'
    """
    cursor.execute(sql)
    completed_services = cursor.fetchall()
    
    if completed_services:
        print("\n--- Completed Room Services ---")
        print(f"{'Room Service ID':<15} | {'Booking ID':<12} | {'Service ID':<10} | {'Service Type':<15} | {'Status':<10} | {'Request Time':<20} | {'Completion Time':<20} | {'Completed By':<15}")
        print("-" * 150)
        for service in completed_services:
            room_service_id, booking_id, service_id, status, request_time, completion_time, service_type, completed_by = service
            request_time = request_time.strftime('%Y-%m-%d %H:%M:%S') if request_time else 'N/A'
            completion_time = completion_time.strftime('%Y-%m-%d %H:%M:%S') if completion_time else 'N/A'
            completed_by = completed_by if completed_by else 'N/A'
            print(f"{room_service_id:<15} | {booking_id:<12} | {service_id:<10} | {service_type:<15} | {status:<10} | {request_time:<20} | {completion_time:<20} | {completed_by:<15}")
        print("-" * 150)
    else:
        print("No completed room services.")
    
    cursor.close()



def staff_menu(connection, staff_id):
    while True:
        print("\n--- Staff Menu ---")
        print("1. Handle Check-In")
        print("2. Handle Check-Out")
        print("3. Provide Room Service")
        print("4. Update Room Status")
        print("5. View Completed Services")
        print("6. Rooms Which need Maintenance ")
        print("7. Sign Out / Switch User")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            handle_checkin(connection)
        elif choice == '2':
            handle_checkout(connection)
        elif choice == '3':
            provide_room_service(connection, staff_id)
        elif choice == '4':
            update_room_status(connection)
        elif choice == '5':
            view_completed_services(connection)
        elif choice == '6':
            view_serviceable_rooms(connection)
        elif choice == '7':
            print("Signing out...")
            return 'signout'
        elif choice == '8':
            print("Exiting...")
            return 'exit'
        else:
            print("Invalid choice. Please try again.")
