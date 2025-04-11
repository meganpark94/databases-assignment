from datetime import datetime
from flights_helpers import display_flights, generate_flight_number, get_departure_time, get_flight, get_flight_duration, select_airport
from menu import clear_console, create_menu
import sqlite3
from pilots import assign_pilot_to_flight, view_assigned_flights

date_format = "%Y-%m-%d %H:%M:%S"

# function to display the top-level 'flights' menu - 'Flight Management' - and handle user 
# selection. Accepts the previous_menu to allow the user to return to the main
# menu. Defines a nested function 'return_to_flights_menu' that redisplays the
# 'Flight Management' menu. Calls 'create_menu' to print the menu and handle 
# user input
def display_flights_menu(previous_menu):
    def return_to_flights_menu():
        display_flights_menu(previous_menu)
    flights_menu = {
        "heading": "=== Flight Management Menu ===",
        "1": ("Update a flight", lambda: update_flights_menu(return_to_flights_menu)),
        "2": ("Schedule a flight", schedule_a_flight),
        "3": ("View flights by criteria", lambda: view_flights_menu(return_to_flights_menu)),
        "4": ("Return to Previous Menu", lambda: create_menu(previous_menu)),
    }
    clear_console()
    create_menu(flights_menu, previous_menu)
  
# function to display the 'Update a Flight' menu and handle user 
# selection. Accepts the previous_menu to allow the user to return to the 'Flight 
# Management' menu. Calls 'create_menu' to print the menu and handle user input. 
def update_flights_menu(previous_menu):
    update_flights_menu = {
        "heading": "=== Update a Flight Menu ===",
        "1": ("Change the departure time of a flight", change_departure_time),
        "2": ("Cancel a flight", cancel_a_flight), 
        "3": ("Assign a pilot to a flight", lambda: assign_pilot_to_flight()),
        "4": ("Update flight destination", update_flight_destination),
        "5": ("Return to Previous Menu", lambda: previous_menu()),
    }
    clear_console()
    create_menu(update_flights_menu, previous_menu)

# function to display the 'View Flights by Criteria' menu and handle user 
# selection. Accepts the previous_menu to allow the user to return to the 'Flight 
# Management' menu. Calls 'create_menu' to print the menu and handle user input. 
def view_flights_menu(previous_menu):
    view_flights_menu = {
        "heading": "=== View Flights by Criteria Menu ===",
        "1": ("View flights assigned to a pilot", view_assigned_flights), # may be able to call function in pilots
        "2": ("View flights to a specific destination", view_flights_to_destination),
        "3": ("View all cancelled flights", view_cancelled_flights), # including cancel
        "4": ("Sort flights by duration", sort_flights_by_duration),
        "5": ("Return to Previous Menu", lambda: previous_menu()),
    }
    clear_console()
    create_menu(view_flights_menu, previous_menu)

# function to update the departure time of a flight. Calls 'get_flight' and 'get_departure_time'
# to retrieve the flight to be updated and the new departure time from the user. Finds the duration of 
# the flight then updates both the departure and arrival time accordingly and displays a success message to the user
def change_departure_time():
    flight_to_update = get_flight("change the departure time for", is_future=True)
    flight_id = flight_to_update[0]
    new_departure_time = get_departure_time(flight_to_update, existing_flight=True)
    old_departure_time = flight_to_update[3]
    old_arrival_time = flight_to_update[5]
    flight_duration = new_departure_time - datetime.strptime(old_departure_time, date_format)
    new_arrival_time = datetime.strptime(old_arrival_time, date_format) + flight_duration
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE flights
        SET departure_time = ?, arrival_time = ?
        WHERE flight_id = ?
    ''', (new_departure_time, new_arrival_time, flight_id)
    )    
    conn.commit()
    conn.close()
    flight_number = flight_to_update[1]
    clear_console()
    print(f"Flight {flight_number} departure time updated to {new_departure_time}. Arrival time updated to {new_arrival_time} accordingly.")

# function to change the status of a flight to 'cancelled'. Calls 'get_flight' to retrieve the flight to be cancelled from the user. 
# Asks the user to confirm they wish to cancel the flight. Displays a success message to the user after they choose to cancel the flight, 
# or returns to the 'Update a flight' menu if the user opts not to cancel the flight
def cancel_a_flight():
    flight_to_update = get_flight("cancel", exclude_status="cancelled", is_future=True)
    flight_id = flight_to_update[0]
    flight_number = flight_to_update[1]
    while True:
        confirmation = input(f"\nPlease confirm that you wish to cancel flight {flight_number} (y/n):")
        if confirmation.lower() == "n":
            clear_console()
            print("\nCancellation aborted.")
            return
        if confirmation.lower() == "y":
            break
        else:
            clear_console()
            print("Invalid choice, please enter 'y' or 'n' to confirm cancellation")
            continue
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("UPDATE flights SET status = ? WHERE flight_id = ?", ("cancelled", flight_id))    
    conn.commit()
    conn.close()
    clear_console()
    print(f"Flight {flight_number} has been cancelled.")

# function to enable the user to update the destination of a scheduled flight. Calls 'get_flight' to retrieve
# a flight to update from the user, excluding already departed or cancelled flights. Calls 'select_airport' to
# retrieve a new destination airport from the user, excluding the departure airport from the avaliable options. 
# Updates the 'arrival_airport_id' of the corresponding flight accordingly, then displays a success message to the
# user.
def update_flight_destination():
    flight_to_update = get_flight("change the destination for", is_future=True, exclude_status="cancelled")
    flight_id = flight_to_update[0]
    conn = sqlite3.connect('flight_management')
    departure_airport_id = conn.execute("SELECT departure_airport_id FROM flights WHERE flight_id = ?", (flight_id,)).fetchone()[0]
    new_destination = select_airport(departure_airport_id)
    new_airport_id = new_destination[0]
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE flights
        SET arrival_airport_id = ?
        WHERE flight_id = ?
    ''', (new_airport_id, flight_id)
    )    
    conn.commit()
    conn.close()
    flight_number = flight_to_update[1]
    clear_console()
    print(f"Flight {flight_number} destination updated to {new_destination[1]} ({new_destination[2]}), {new_destination[3]}, {new_destination[4]}.")


# function to enable the user to schedule a new flight. Calls 'select_airport' and 'get_departure_time' to retrieve an
# airport and departure time from the user. Calls 'select_airport' with the chosen departure_airport as an argument, 
# which excludes the departure_airport from the list of available aiports to choose from. Calculates the arrival_time 
# by calling 'get_flight_duration' to retrieve a flight duration from the user and adding the timedelta to the departure_time.
# Inserts the new flight into the database and prints a success message to the user             
def schedule_a_flight():
    clear_console()
    print("===========Schedule a flight==========")
    departure_airport = select_airport()
    departure_airport_id = departure_airport[0]
    departure_time = get_departure_time(airport=departure_airport)
    arrival_airport = select_airport(departure_airport_id=departure_airport_id)
    arrival_airport_id = arrival_airport[0]
    arrival_time = departure_time + get_flight_duration()
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    flight_number = generate_flight_number()
    cursor.execute('''
        INSERT INTO flights (flight_number, departure_airport_id, arrival_airport_id, departure_time, arrival_time)
        VALUES (?, ?, ?, ?, ?)
    ''',(flight_number, departure_airport_id, arrival_airport_id, departure_time, arrival_time)
    )
    conn.commit()
    conn.close()
    clear_console()
    print(f"\nFlight to {arrival_airport[3]}, {arrival_airport[4]} scheduled successfully.\n"
          f"Departing from {departure_airport[1]} at {departure_time}\n"
          f"Arriving at {arrival_airport[1]} at {arrival_time}")

# function to retrive any existing flights to a user-provided city or country. 
def view_flights_to_destination():
    clear_console()
    print("========== View flights to a given destination ==========")
    provided_location = input("Please enter a city or country to view any existing flights to that location: ").strip()
    columns = [
        "f.flight_number",
        "departure_airport.airport_name AS departure_airport",
        "f.departure_time",
        "arrival_airport.airport_name AS arrival_airport",
        "f.arrival_time",
        "d.city",
        "d.country"
    ]
    if provided_location == "":
        print("\nYou did not provide a location. Displaying flights to all saved locations...\n")
    else:
        print(f"\n==========Flights to {provided_location}==========")
    display_flights(columns = columns, destination=provided_location)
   
# function to view all cancelled flights. Calls 'display_flights' to print the relevant flight details for 
# cancelled flights, or an informative message if no cancelled flights exist
def view_cancelled_flights():
    clear_console()
    print("========== Cancelled flights ==========")
    display_flights(status="cancelled")
    

# function to fetch and display all saved flights in descending order of duration
def sort_flights_by_duration():
    clear_console()
    print("========== Flights - longest to shortest duration ==========")
    query = '''
        SELECT 
        f.flight_id, 
        f.flight_number, 
        d.airport_name AS d,
        f.departure_time, 
        a.airport_name AS a,
        f.arrival_time, 
        (julianday(arrival_time) - julianday(departure_time)) * 24 * 60 AS duration_minutes
        FROM flights AS f
        JOIN airports AS d ON f.departure_airport_id = d.airport_id
        JOIN airports AS a ON f.arrival_airport_id = a.airport_id
        ORDER BY duration_minutes DESC;
    '''
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute(query)
    flights = cursor.fetchall()
    conn.close()
    if not flights:
        print("\nNo flights found.")
    for flight in flights:
        flight_id, flight_number, departure_airport, departure_time, arrival_airport, arrival_time, duration = flight
        print(f"Flight {flight_number} | Departure: {departure_airport}, {departure_time} | Arrival: {arrival_airport}, {arrival_time} | Duration: {int(duration)} minutes.")
        print("-" * 50)
    

    