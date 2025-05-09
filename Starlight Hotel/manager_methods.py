from db_connection import create_connection
import mysql.connector
from decimal import Decimal
from datetime import datetime

def view_pending_bookings(connection):
    cursor = connection.cursor()
    sql = """
    SELECT b.BookingID, u.Username, r.RoomID, r.RoomType, b.CheckInDate, b.CheckOutDate, b.BookingStatus
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingStatus = 'Pending'
    """
    cursor.execute(sql)
    pending_bookings = cursor.fetchall()
    
    if pending_bookings:
        print("\n--- Pending Bookings ---")
        print(f"{'Booking ID':<12} | {'Username':<15} | {'Room Number':<12} | {'Room Type':<10} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Status':<10}")
        print("-" * 110)
        for booking in pending_bookings:
            booking_id, username, room_id, room_type, check_in_date, check_out_date, status = booking
            check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
            check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
            print(f"{booking_id:<12} | {username:<15} | {room_id:<12} | {room_type:<10} | {check_in_date:<15} | {check_out_date:<15} | {status:<10}")
        print("-" * 110)
        return True
    else:
        print("No pending bookings.")
        return False
    
    cursor.close()

def approve_booking(connection, booking_id):
    cursor = connection.cursor()
    
    sql_get_room_id = "SELECT RoomID FROM Bookings WHERE BookingID = %s"
    cursor.execute(sql_get_room_id, (booking_id,))
    room_id = cursor.fetchone()
    
    if room_id:
        room_id = room_id[0] 
        sql_update_booking = "UPDATE Bookings SET BookingStatus = 'Approved' WHERE BookingID = %s"
        cursor.execute(sql_update_booking, (booking_id,))
        
        sql_update_room = "UPDATE Rooms SET Availability = 'Booked' WHERE RoomID = %s"
        cursor.execute(sql_update_room, (room_id,))
        
        connection.commit()
        print("Booking approved and room status updated to 'Booked'.")
    else:
        print("Invalid Booking ID.")
    
    cursor.close()

def reject_booking(connection, booking_id):
    cursor = connection.cursor()
    
    sql_get_room_id = "SELECT RoomID FROM Bookings WHERE BookingID = %s"
    cursor.execute(sql_get_room_id, (booking_id,))
    room_id = cursor.fetchone()
    
    if room_id:
        room_id = room_id[0] 
        sql_update_booking = "UPDATE Bookings SET BookingStatus = 'Rejected' WHERE BookingID = %s"
        cursor.execute(sql_update_booking, (booking_id,))
        
        connection.commit()
        print("Booking rejected.")
    else:
        print("Invalid Booking ID.")
    
    cursor.close()

def view_room_availability(connection):
    cursor = connection.cursor()
    sql = "SELECT RoomID, RoomType, Availability FROM Rooms"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    
    if rooms:
        print("\n--- Rooms ---")
        print(f"{'Room ID':<10}{'Room Type':<15}{'Availability':<15}")
        print("-" * 50)
        for room in rooms:
            room_id, room_type, availability = room
            print(f"{room_id:<10}{room_type:<15}{availability:<15}")
        print("-" * 50)
        input("Press Enter to go to the Main Menu")
    else:
        print("No rooms available.")
        
    cursor.close()

def generate_daily_activity_reports(connection):
    cursor = connection.cursor()
    
    current_date = datetime.now().date()

    sql_checkins = "SELECT COUNT(*) FROM Bookings WHERE DATE(CheckedInTime) = %s"
    sql_checkouts = "SELECT COUNT(*) FROM Bookings WHERE DATE(CheckedOutTime) = %s"
    
    cursor.execute(sql_checkins, (current_date,))
    checkins_count = cursor.fetchone()[0]
    
    cursor.execute(sql_checkouts, (current_date,))
    checkouts_count = cursor.fetchone()[0]

    
    sql_bookings = """
    SELECT BookingStatus, COUNT(*)
    FROM Bookings
    WHERE DATE(CreatedAt) = %s
    GROUP BY BookingStatus
    """
    cursor.execute(sql_bookings, (current_date,))
    bookings_summary = cursor.fetchall()
    
    
    sql_room_availability = """
    SELECT Availability, COUNT(*)
    FROM Rooms
    GROUP BY Availability
    """
    cursor.execute(sql_room_availability)
    room_availability = cursor.fetchall()
    
   
    sql_room_services = """
    SELECT Status, COUNT(*)
    FROM RoomServices
    WHERE DATE(RequestTime) = %s OR DATE(CompletionTime) = %s
    GROUP BY Status
    """
    cursor.execute(sql_room_services, (current_date, current_date))
    room_services_summary = cursor.fetchall()
    
    
    sql_financial_summary = """
    SELECT 
        SUM(b.TotalCost) AS TotalRoomRevenue,
        SUM(CASE WHEN rs.Status = 'Completed' THEN s.Price ELSE 0 END) AS TotalServiceRevenue,
        SUM(b.TotalCost + CASE WHEN rs.Status = 'Completed' THEN s.Price ELSE 0 END) AS TotalRevenue
    FROM Bookings b
    LEFT JOIN RoomServices rs ON b.BookingID = rs.BookingID
    LEFT JOIN Services s ON rs.ServiceID = s.ServiceID
    WHERE DATE(b.CreatedAt) = %s
    """
    cursor.execute(sql_financial_summary, (current_date,))
    financial_summary = cursor.fetchone()
    
    total_room_revenue = financial_summary[0] if financial_summary[0] is not None else 0.0
    total_service_revenue = financial_summary[1] if financial_summary[1] is not None else 0.0
    total_revenue = financial_summary[2] if financial_summary[2] is not None else 0.0

    print("\n" + "="*50)
    print("           Daily Activity Report")
    print("="*50)
    print(f"Date: {current_date}")
    print("-" * 50)
    print(f"Check-ins Today: {checkins_count}")
    print(f"Check-outs Today: {checkouts_count}")
    print("\nBookings Summary:")
    for status, count in bookings_summary:
        print(f"{status}: {count}")
    print("\nRoom Availability:")
    for availability, count in room_availability:
        print(f"{availability}: {count}")
    print("\nRoom Services Summary:")
    for status, count in room_services_summary:
        print(f"{status}: {count}")
    print(f"\nTotal Revenue: ${total_revenue:.2f}")
    print(f"Revenue from Room Bookings: ${total_room_revenue:.2f}")
    print(f"Revenue from Services: ${total_service_revenue:.2f}")
    print("="*50)
    
    print("Press Enter to go back to the main menu")
    input()
    
    cursor.close()

def generate_bill(connection):
    cursor = connection.cursor()
    

    sql_checked_out = """
    SELECT b.BookingID, u.Username, r.RoomID, b.CheckInDate, b.CheckOutDate, b.TotalCost
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingStatus = 'Checked Out'
    """
    cursor.execute(sql_checked_out)
    bookings = cursor.fetchall()
    
    if not bookings:
        print("No checked-out bookings found.")
        cursor.close()
        return
    
    print("\n--- Checked-Out Bookings ---")
    print(f"{'Booking ID':<12} | {'Username':<15} | {'Room ID':<10} | {'Check-In Date':<15} | {'Check-Out Date':<15} | {'Total Cost':<10}")
    print("-" * 90)
    for booking in bookings:
        booking_id, username, room_id, check_in_date, check_out_date, total_cost = booking
        check_in_date = check_in_date.strftime('%Y-%m-%d') if check_in_date else 'N/A'
        check_out_date = check_out_date.strftime('%Y-%m-%d') if check_out_date else 'N/A'
        total_cost = f"${total_cost:.2f}" if total_cost is not None else 'N/A'
        print(f"{booking_id:<12} | {username:<15} | {room_id:<10} | {check_in_date:<15} | {check_out_date:<15} | {total_cost:<10}")
    print("-" * 90)
    
    booking_id = input("Enter Booking ID to generate bill: ")
    
    
    sql_validate_booking = """
    SELECT b.BookingID, u.Username, r.RoomID, b.CheckInDate, b.CheckOutDate, b.TotalCost
    FROM Bookings b
    JOIN Users u ON b.UserID = u.UserID
    JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingID = %s AND b.BookingStatus = 'Checked Out'
    """
    cursor.execute(sql_validate_booking, (booking_id,))
    booking = cursor.fetchone()
    
    if not booking:
        print("Invalid Booking ID or Booking is not checked out.")
        cursor.close()
        return
    
    booking_id, username, room_id, check_in_date, check_out_date, room_total_cost = booking
    
    
    num_days = (check_out_date - check_in_date).days
    num_nights = num_days
    
    
    sql_services = """
    SELECT rs.ServiceID, s.ServiceType, s.Price
    FROM RoomServices rs
    JOIN Services s ON rs.ServiceID = s.ServiceID
    WHERE rs.BookingID = %s AND rs.Status = 'Completed'
    """
    cursor.execute(sql_services, (booking_id,))
    services = cursor.fetchall()
    
    
    total_service_cost = sum(service[2] for service in services)
    
    
    total_cost = room_total_cost + total_service_cost
    
    
    pst_rate = Decimal('0.08')
    pst_amount = total_cost * pst_rate
    final_total_cost = total_cost + pst_amount
    
    
    print("\n" + "="*50)
    print("           Starlight Hotel")
    print("     Where stars meet comfort")
    print("="*50)
    print(f"Booking ID: {booking_id}")
    print(f"Customer: {username}")
    print(f"Room ID: {room_id}")
    print(f"Check-In Date: {check_in_date.strftime('%Y-%m-%d')}")
    print(f"Check-Out Date: {check_out_date.strftime('%Y-%m-%d')}")
    print(f"Duration of Stay: {num_days} Days and {num_nights} Nights")
    print("="*50)
    print("Services:")
    print(f"{'Service ID':<12} | {'Service Type':<20} | {'Price':<10}")
    print("-" * 45)
    for service in services:
        service_id, service_type, price = service
        print(f"{service_id:<12} | {service_type:<20} | ${price:<10.2f}")
    print("-" * 45)
    print(f"Room Cost: ${room_total_cost:.2f}")
    print(f"Total Service Cost: ${total_service_cost:.2f}")
    print(f"PST (8%): ${pst_amount:.2f}")
    print(f"Total Cost: ${final_total_cost:.2f}")
    print("="*50)
    print("Thank you for choosing Starlight Hotel!")
    print("="*50)
    
    print("Press Enter to go back to the main menu")
    input()
    
    cursor.close()

def handle_booking_approval_rejection(connection):
    if not view_pending_bookings(connection):
        return
    
    while True:
        booking_id = input("Enter Booking ID to approve or reject (or press 0 to go back to the main menu): ")
        
        if booking_id == '0':
            return

        cursor = connection.cursor()
        sql_validate_booking = "SELECT BookingID FROM Bookings WHERE BookingID = %s AND BookingStatus = 'Pending'"
        cursor.execute(sql_validate_booking, (booking_id,))
        valid_booking = cursor.fetchone()
        cursor.close()

        if not valid_booking:
            print("Invalid Booking ID. Please enter a valid pending Booking ID.")
            continue

        while True:
            print("\n1. Approve Booking")
            print("2. Reject Booking")
            choice = input("Enter your choice: ")
            
            if choice == '1':
                approve_booking(connection, booking_id)
                break
            elif choice == '2':
                reject_booking(connection, booking_id)
                break
            else:
                print("Invalid choice. Please try again.")
        
        break

def manager_menu(connection):
    while True:
        print("\n--- Manager Menu ---")
        print("1. Bookings")
        print("2. View Room Availability")
        print("3. Generate Daily Activity Reports")
        print("4. Generate Bill for Customer")
        print("5. Sign Out / Switch User")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            handle_booking_approval_rejection(connection)
        elif choice == '2':
            view_room_availability(connection)
        elif choice == '3':
            generate_daily_activity_reports(connection)
        elif choice == '4':
            generate_bill(connection)
        elif choice == '5':
            print("Signing out...")
            return 'signout'
        elif choice == '6':
            print("Exiting...")
            return 'exit'
        else:
            print("Invalid choice. Please try again.")