from datetime import datetime, timedelta
import random
from destinations import display_airports_and_destinations
from menu import clear_console, create_menu
import sqlite3
from pilots import display_pilots

date_format = "%Y-%m-%d %H:%M:%S"

# function to display the top-level 'flights' menu - 'Flight Management' - and handle user 
# selection. Accepts the previous_menu to allow the user to return to the main
# menu. Defines a nested function `return_to_flights_menu` that redisplays the
# 'Flight Management' menu. Calls 'create_menu' to print the menu and handle 
# user input. 
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
    "2": ("Cancel a flight", cancel_a_flight), # including cancel
    "3": ("Assign a pilot to a flight", assign_update_pilot),
    "4": ("Update flight destination", update_flight_destination),
    "5": ("Return to Previous Menu", lambda: previous_menu()),
    }
    clear_console()
    create_menu(update_flights_menu, previous_menu)

    
# function to update the departure time of a flight. Calls 'get_flight' and 'get_departure_time'
# to retrieve the flight to be updated and the new departure time from the user.
# to be updated from the user. Finds the duration of the flight then updates both the departure 
# and arrival time accoredingly. Displays a success message to the user.
def change_departure_time():
    flight_to_update = get_flight("change the departure time for", columns=["flight_id", "flight_number", "departure_time", "arrival_time"], is_future=True)
    flight_id = flight_to_update[0]
    new_departure_time = get_departure_time(flight_to_update)
    old_departure_time = flight_to_update[2]
    old_arrival_time = flight_to_update[3]
    flight_duration = new_departure_time - datetime.strptime(old_departure_time, date_format)
    new_arrival_time = datetime.strptime(old_arrival_time,date_format) + flight_duration
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute('''UPDATE flights
        SET departure_time = ?, arrival_time = ?
        WHERE flight_id = ?
    ''', (new_departure_time, new_arrival_time, flight_id))    
    conn.commit()
    conn.close()
    flight_number = flight_to_update[1]
    clear_console()
    print(f"Flight {flight_number} departure time updated to {new_departure_time}. Arrival time updated to {new_arrival_time} accordingly.")

# function to change the status of a flight to 'cancelled'. Calls 'get_flight' to
# retrieve the flight to be cancelled from the user. Asks the user to confirm they wish to cancel the flight. 
# Displays a success message to the user after they choose to cancel the flight, or returns to the 'Update a flight' menu if the user
# opts not to cancel the flight.
def cancel_a_flight():
    flight_to_update = get_flight("cancel", columns=["flight_id", "flight_number", "status"], exclude_status="cancelled")
    while True:
        flight_id = flight_to_update[0]
        flight_number = flight_to_update[1]
        confirmation = input(f"\nPlease confirm that you wish to cancel flight {flight_number} (y/n):")
        if confirmation.lower() == "n":
            clear_console()
            print("\nCancellation aborted")
            return
        if confirmation.lower() == "y":
            break
        else:
            print("Invalid choice, please enter 'y' or 'n' to confirm cancellation")
            continue

    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute('''UPDATE flights
        SET status = ?
        WHERE flight_id = ?
    ''', ("cancelled", flight_id))    
    conn.commit()
    conn.close()
    clear_console()
    print(f"Flight {flight_number} has been cancelled.")
        
# helper function to fetch the flight details of a flight. Calls 'display_flights' with the provided
# arguments, making the function reusable. Asks the user to input the ID of the flight they want to update,
# verifies it's a valid flight_id and that it matches the criteria passed in (if provided), the returns the
# flight details as a tuple.
def get_flight(type, columns=None, pilot=None, is_future=None, departure_date=None, exclude_status=None):
    clear_console()
    if is_future:
        header = "========== Upcoming Flights=========="
    else: 
        header = "==========Flights=========="
    print(header)
    flights = display_flights(columns=columns, pilot=pilot, is_future=is_future, departure_date=departure_date, exclude_status=exclude_status)
    while True:
        flight_id = input(f"\nPlease enter the flight_id of the flight you'd like to {type}: ")
        try: 
            flight_id = int(flight_id)
        except ValueError:
            clear_console()
            print(header + flights + flight_id + "\nInvalid input. Please enter a valid flight ID.")
            continue
        flight = next((flight for flight in flights if flight[0] == flight_id), None)
        if flight:
            return flight
        else: 
            print(header + flights + flight_id + "\nInvalid flight ID, please try again.")

# helper function to prompt the user to confirm that they wish to assign a pilot to a flight
# when the flight already has a pilot assigned.
def confirm_pilot_update(current_pilot_name, current_pilot_id, flight_number):
    while True:
        clear_console()
        print(f"\nPilot {current_pilot_name} (ID: {current_pilot_id}) is currently assigned to flight {flight_number}.")
        choice = input("\nDo you want to update the assigned pilot? (y/n): ")
        if choice.lower() == "n":
            clear_console()
            print("\nUpdate pilot assignement aborted.")
            return False
        if choice.lower() == "y":
            clear_console()
            return True
        print("\nInvalid choice, please enter 'y' or 'n' to indicate your choice.")

# helper function to retrive a departure time from the user. Used for updating the departure time of existing flights, 
# and when scheduling new flights. Ensures the departrue time is not in the past and is in the accepted format before 
# returning the departure time as a datetime object. 
def get_departure_time(flight=None, airport=None, existing_flight=None):
    while True:
        if existing_flight:
            departure_time = input(f"\nPlease enter a new departure time for flight {flight[1]}(YYYY-MM-DD HH:MM:SS): ")
        else: 
            departure_time = input(f"\nPlease enter the departure time for flight from {airport[1]}(YYYY-MM-DD HH:MM:SS): ")
        try: 
            departure_time = datetime.strptime(departure_time, date_format)
        except ValueError:
            clear_console()
            print(str(departure_time) + "\nInvalid departure time format. Please use the format 'YYYY-MM-DD HH:MM:SS'.")
            continue
        if departure_time <= datetime.now():
            clear_console()
            print(str(departure_time) + "\nInvalid input. The provided departure time must be in the future.")
            continue
        clear_console()
        return departure_time

# helper function to retrive the pilot assigned to a specific flight. Returns the id and name of the 
# pilot currently assigned to a flight. If no pilot is yet assigned, returns None. 
def get_current_pilot(flight):
    current_pilot_id = flight[2]
    if not current_pilot_id:
        return None, None
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM pilots WHERE pilot_id = ?", (current_pilot_id,))
    current_pilot_name = cursor.fetchone()
    conn.close()
    if current_pilot_name:
        return current_pilot_id, f"{current_pilot_name[0]} {current_pilot_name[1]}"
    return current_pilot_id, "Unknown Pilot."

# helper function to retrive a pilot from the user. Calls 'display_pilots' with the provided arguments
# to ensure only the relevant piolots are displayed. Ensures the pilot_id exists and meets the criteria before
# returning the pilot id and name
def select_pilot(departure_time, arrival_time, flight_number):
    while True:
        clear_console()
        print("==========Available Pilots==========\n")
        pilots = display_pilots(only_available=True, departure_time=departure_time, arrival_time=arrival_time)
        pilot_id = input(f"\nPlease enter the pilot_id of the pilot you'd like to assign to flight {flight_number}: ")
        try: 
            pilot_id = int(pilot_id)
        except ValueError:
            print("\nInvalid input. Please enter a valid pilot ID.")
            continue
        pilot_to_assign = next((pilot for pilot in pilots if pilot[0] == pilot_id), None)
        if pilot_to_assign:
            return pilot_id, f"{pilot_to_assign[1]} { pilot_to_assign[2]}"
        else: 
            print("\nInvalid pilot ID, please try again.")

# function to assign a pilot to a flight. Calls 'get_flight' to retrive a valid flight from the user, ensuring
# pilots cannot be assigned to past or cancelled flights. Calls 'get_current_pilot' and, if a pilot is already 
# assigned to the flight, calls confirm_pilot_update to prompt hte user to conofim they wish to replace the 
# currently assigned pilot with a new one. Calls 'select_pilot' to retrive a pilot to assign from the user. 
# Updates the database and prints a success message to the user. 
def assign_update_pilot():
    flight_to_update = get_flight("assign a pilot to", columns=["flight_id", "flight_number", "pilot_id", "departure_time", "arrival_time"], exclude_status="cancelled")
    flight_id, flight_number, departure_time, arrival_time = flight_to_update[0], flight_to_update[1], flight_to_update[3], flight_to_update[4]
    current_pilot_id, current_pilot_name = get_current_pilot(flight_to_update)
    if current_pilot_id:
        update_assigned_pilot = confirm_pilot_update(current_pilot_name, current_pilot_id, flight_number)  
        if not update_assigned_pilot:
            return      
    pilot_id, pilot_name = select_pilot(departure_time, arrival_time, flight_number)
    conn = sqlite3.connect('flight_management')
    conn.execute("UPDATE flights SET pilot_id = ? WHERE flight_id = ?", (pilot_id, flight_id) )
    conn.commit()
    conn.close()
    clear_console()
    print(f"Pilot {pilot_name} has been assigned to flight {flight_number}.\n")


def update_flight_destination():
    print("x")
# helper function to retrieve an airport from the user. Calls 'display_airports_and_destinations' to display the
# available airports, then checks the airport exists and is valid before returning the airport details as a tuple. 
def select_airport(departure_airport_id=None):
    while True:
        airports= display_airports_and_destinations(departure_airport_id)
        if not departure_airport_id:
            airport_id = input(f"\n===Choose Departure Airport===\nPlease enter the Airport ID of the airport to depart from: ")
        else: airport_id = input(f"\n===Choose Arrival Airport===\nPlease enter the Airport ID of the arrival airport: ")
        try: airport_id = int(airport_id)
        except ValueError:
            print("\nInvalid input. Please enter a valid Airport ID.")
            continue
        chosen_airport = next((airport for airport in airports if airport[0] == airport_id), None)
        if chosen_airport:
            return chosen_airport
        else: print("\nInvalid Airport ID, please try again.")


# helper function to generate a random flight number. Chooses a random airline code from 
# a list and concatentates with a random 3 or 4 digit number to create a flight number. Checks the
# flight number does not already exist in the database then returns it as a string. 
def generate_flight_number():
    airline_codes = ["NY", "LA", "LD", "TP", "BC", "KJ", "IB", "EN"]
    flight_number = random.choice(airline_codes) + str(random.randint(100,9999))
    while True:
        conn = sqlite3.connect("flight_management")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM flights WHERE flight_number = ?", (flight_number,))
            exists = cursor.fetchone()[0] > 0
            if not exists:
                return flight_number
        finally:
            conn.close()

# helper function to retieve the duration of a flight from the user. Checks that the provided hours and minutes are positive integers,
# and total less than 36 hours. Also checks that the value provided for minutes is less than 60. Retuns the duration as a timedelta object. 
# This is used when scheduling a flight to calculate the arrival time.
def get_flight_duration():
    clear_console()
    print("To enter the duration of the flight, please enter the hours first, then the minutes. The arrival time will be scheduled accordingly.")
    while True:
        try:
            hours = int(input("\nPlease enter flight duration (hours): "))
            minutes = int(input("Please enter the additional minutes: "))
            if hours < 0 or minutes < 0:
                clear_console()
                print(f"Provided flight duration: {hours} hours, {minutes} minutes\nInvalid duration. Duration must be a positive value.\n")
                continue
            if minutes > 60:
                clear_console()
                print(f"Provided flight duration: {hours} hours, {minutes} minutes\nInvalid duration. Minutes must be less than 60.\n")
                continue
            total_duration = timedelta(hours=hours, minutes=minutes)
            if total_duration > timedelta(hours=36):
                clear_console()
                print(f"Provided flight duration: {hours} hours, {minutes} minutes\nInvalid duration. Total flight duration cannot exceed 36 hours.\n")
                continue
            return total_duration
        except ValueError:
            clear_console()
            print("Invalid input. Please enter numbers only.")

# function to enable the user to schedule a new flight. Calls 'select_airport' and 'get_departure_time' to retrieve an
# airport and departure time from the user. Calls 'select_airport' with the chosen departure_airport as an argument, 
# which excludes the departure_airport from the list of available aiports to choose from. Calculates the arrival_time 
# by calling 'get_flight_duration' to retrieve a flight duration from the user and adding the timedelta to the departure_time.
# Inserts the new flight into the database and prints a success message to the user.              
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
    cursor.execute('''INSERT INTO flights (flight_number, departure_airport_id, arrival_airport_id, departure_time, arrival_time)
                      VALUES (?, ?, ?, ?, ?)''',
                   (flight_number, departure_airport_id, arrival_airport_id, departure_time,
                    arrival_time))
    conn.commit()
    conn.close()

    clear_console()
    print(f"\nFlight to {arrival_airport[3]}, {arrival_airport[4]} scheduled successfully.\n"
          f"Departing from {departure_airport[1]} at {departure_time}\n"
          f"Arriving at: {arrival_airport[1]} at {arrival_time}")

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

def view_assigned_flights():
    print("x")

# function to retrive any existing flights to a user provided city or country. 
def view_flights_to_destination():
    clear_console()
    print("========== View flights to a given destination ==========")
    provided_location = input("Please enter a city or country to view any existing flights to that location: ").strip()
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    query = '''SELECT f.flight_id, f.flight_number, f.departure_time, f.arrival_time, departure_airport.airport_name, arrival_airport.airport_name, d.city, d.country
        FROM flights AS f
        JOIN airports AS departure_airport ON f.departure_airport_id = departure_airport.airport_id
        JOIN airports AS arrival_airport ON f.arrival_airport_id = arrival_airport.airport_id
        JOIN destinations AS d ON arrival_airport.destination_id = d.destination_id
        WHERE d.city LIKE ? OR d.country LIKE ?
        '''
    cursor.execute(query, ('%' + provided_location + '%','%' + provided_location + '%',)) 
    flights = cursor.fetchall()
    conn.close()
    if not flights:
        print(f"\nNo flights found to {provided_location}.")
        return
    print(f"\n==========Flights to {provided_location}==========\n")
    for flight in flights:
        flight_id, flight_number, departure_time, arrival_time, departure_airport, arrival_airport, city, country = flight
        print(f"Flight number: {flight_number} | Departure Airport: {departure_airport} | Departure: {departure_time}")
        print(f"Arrival airport: {arrival_airport} | Arrival: {arrival_time} | Destination: {city}, {country}")
        print("-" * 50)

# function to view all cancelled flights. Calls 'display_' flights to print the relevant flight details for 
# cancelled flights, or an informative message if no cancelled flights exist. 
def view_cancelled_flights():
    clear_console()
    print("========== Cancelled flights ==========")
    display_flights(columns=["flight_number","departure_time", "arrival_time", "status"], status="cancelled")

# function to sort all saved flights in descending order of duration.
def sort_flights_by_duration():
    clear_console()
    print("========== Flights - longest to shortest duration ==========")
    query = '''SELECT 
    flight_id, 
    flight_number, 
    departure_time, 
    arrival_time, 
    (julianday(arrival_time) - julianday(departure_time)) * 24 * 60 AS duration_minutes
FROM flights
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
        flight_id, flight_number, departure_time, arrival_time, duration = flight
        print(f"Flight {flight_number} | Departure: {departure_time} | Arrival: {arrival_time} | Duration: {int(duration)} minutes.")

    



# helper function to display a list of all flights. Accpets a list of columns to display; if None, displays all columns.
# Accepts other arguments to make the function resuable, allowing relevant columns to be displayed. 
def display_flights(columns=None, pilot=None, is_future=None, departure_date=None, exclude_status=None, status=None, destination=None):
    conn = sqlite3.connect('flight_management')
    
    if not columns:
        columns = ["flight_id", "flight_number", "departure_airport_id", "arrival_airport_id", "pilot_id", "departure_time", "arrival_time", "status"]
    
    columns_str = ", ".join(columns)
    query = f"SELECT {columns_str} FROM flights WHERE 1=1"
    params=[]

    if is_future:
        query += " AND departure_time >= CURRENT_TIMESTAMP"

    if departure_date:
        query += " AND DATE(departure_time) = ?"
        params.append(departure_date)

    if pilot:
        query += " AND pilot_id = ?"
        params.append(pilot)

    if exclude_status:
        query += " AND status != ?"
        params.append(exclude_status)
    
    if status:
        query += " AND status = ?"
        params.append(status)


    
    flights = conn.execute(query, params).fetchall()
    conn.close

    if not flights: 
        print("\nNo matching flights found.")
        return None
    
    for flight in flights: 
        print(", ".join(f"{column}: {flight[i]}" for i, column in enumerate (columns)))
    
    return flights


    
    
    