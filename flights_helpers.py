from datetime import datetime, timedelta
import random
import sqlite3

from destinations_helpers import display_airports_and_destinations
from menu import clear_console

date_format = "%Y-%m-%d %H:%M:%S"

# helper function to fetch the flight details of a flight. Calls 'display_flights' with the provided
# arguments, making the function reusable. Asks the user to input the ID of the flight they want to update,
# verifies it's a valid flight_id and that it matches the criteria passed in (if provided), then returns the
# flight details as a tuple
def get_flight(type, columns=None, pilot=None, is_future=None, departure_date=None, exclude_status=None):
    clear_console()
    if is_future:
        header = "========== Upcoming Flights=========="
    else: 
        header = "==========Flights=========="
    print(header)
    flights = display_flights(columns=columns, pilot=pilot, is_future=is_future, departure_date=departure_date, exclude_status=exclude_status)
    while True:
        flight_id = input(f"\nPlease enter the Flight ID of the flight you'd like to {type}: ")
        try: 
            flight_id = int(flight_id)
        except ValueError:
            clear_console()
            print(header)
            flights = display_flights(columns=columns, pilot=pilot, is_future=is_future, departure_date=departure_date, exclude_status=exclude_status)
            print("\nYour input: " + str(flight_id) + "\nInvalid input. Please enter a valid Flight ID.")
            continue
        flight = next((flight for flight in flights if flight[0] == flight_id), None)
        if flight:
            return flight
        else: 
            clear_console()
            print(header)
            flights = display_flights(columns=columns, pilot=pilot, is_future=is_future, departure_date=departure_date, exclude_status=exclude_status)
            print("\nYour input: " + str(flight_id) + "\nInvalid flight ID, please try again.")

# helper function to retrive a departure time from the user. Used for updating the departure time of existing flights
# and when scheduling new flights. Ensures the departure time is not in the past and is in the accepted format before 
# returning the departure time as a datetime object
def get_departure_time(flight=None, airport=None, existing_flight=None):
    while True:
        if existing_flight:
            departure_time = input(f"\nPlease enter a new departure time for flight {flight[1]} (YYYY-MM-DD HH:MM:SS): ")
        else: 
            departure_time = input(f"\nPlease enter the departure time for flight from {airport[1]} (YYYY-MM-DD HH:MM:SS): ")
        try: 
            departure_time = datetime.strptime(departure_time, date_format)
        except ValueError:
            clear_console()
            print("Your input: " + str(departure_time) + "\nInvalid departure time format. Please use the format 'YYYY-MM-DD HH:MM:SS'.")
            continue
        if departure_time <= datetime.now():
            clear_console()
            print("Your input: " + str(departure_time) + "\nInvalid input. The provided departure time must be in the future.")
            continue
        clear_console()
        print(f"Departure time set to: {departure_time}\n")
        return departure_time

# helper function to retrieve an airport from the user. Calls 'display_airports_and_destinations' to display the
# available airports, then checks the airport exists and is valid before returning the airport details as a tuple 
def select_airport(departure_airport_id=None):
    while True:
        airports = display_airports_and_destinations(departure_airport_id)
        if not departure_airport_id:
            airport_id = input(f"\n===Choose Departure Airport===\nPlease enter the Airport ID of the airport to depart from: ")
        else: 
            airport_id = input(f"\n===Choose Arrival Airport===\nPlease enter the Airport ID of the arrival airport: ")
        try: 
            airport_id = int(airport_id)
        except ValueError:
            clear_console()
            print("Your input: " + str(airport_id) + "\nInvalid input. Please enter a valid Airport ID.\n")
            continue
        chosen_airport = next((airport for airport in airports if airport[0] == airport_id), None)
        if chosen_airport:
            clear_console()
            print(f"Airport selected: {chosen_airport[1]}({chosen_airport[2]})")
            return chosen_airport
        else: 
            clear_console()
            print("Your input: " + str(airport_id) + "\nInvalid Airport ID, please try again.\n")

# helper function to generate a random flight number. Chooses a random airline code from 
# a list and concatentates with a random 3 or 4 digit number to create a flight number. Checks the
# flight number does not already exist in the database then returns it as a string
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

# helper function to retrieve the duration of a flight from the user. Checks that the provided hours and minutes are positive integers
# and total less than 36 hours. Also checks that the value provided for minutes is less than 60. Returns the duration as a timedelta object. 
# This is used when scheduling a flight to calculate the arrival time
def get_flight_duration():
    print("\nTo enter the duration of the flight, please enter the hours first, then the minutes. The arrival time will be scheduled accordingly.")
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

# helper function to generate a query string to retrieve flights data from the database. Can be called with various arguments to make the
# function reusable
def build_flights_query(columns=None, pilot=None, is_future=None, departure_date=None, exclude_status=None, status=None, destination=None):
    columns_str = ", ".join(columns)
    query = f'''
        SELECT {columns_str}
        FROM flights AS f
        JOIN airports AS departure_airport ON f.departure_airport_id = departure_airport.airport_id
        JOIN airports AS arrival_airport ON f.arrival_airport_id = arrival_airport.airport_id
        JOIN destinations AS d ON arrival_airport.destination_id = d.destination_id
        WHERE 1=1
    '''
    params=[]
    if is_future:
        query += " AND f.departure_time >= CURRENT_TIMESTAMP"
    if departure_date:
        query += " AND DATE(f.departure_time) = ?"
        params.append(departure_date)
    if pilot:
        query += " AND f.pilot_id = ?"
        params.append(pilot)
    if exclude_status:
        query += " AND f.status != ?"
        params.append(exclude_status)
    if status:
        query += " AND f.status = ?"
        params.append(status)
    if destination:
        query += " AND (d.city LIKE ? OR d.country LIKE ?)"
        params.extend([f"%{destination}%", f"%{destination}%"])
    return query, params

# helper function to display a list of flights in a readable format. Accpets a list of columns to display; if None, displays the defined columns.
# Accepts other arguments to make the function resuable, allowing relevant data to be displayed. Returns retrieved flights as a list of tuples to
# be used by functions which call this one
def display_flights(columns=None, pilot=None, is_future=None, departure_date=None, exclude_status=None, status=None, destination=None):
    if not columns:
        columns = [
            "f.flight_id", "f.flight_number", "departure_airport.airport_name AS departure_airport", "f.departure_time", "arrival_airport.airport_name AS arrival_airport", "f.arrival_time"
        ]
    query, params = build_flights_query(columns, pilot, is_future, departure_date, exclude_status, status, destination)
    conn = sqlite3.connect('flight_management')
    flights = conn.execute(query, params).fetchall()
    conn.close()
    if not flights: 
        print("\nNo matching flights found.")
        return None
    column_names = format_column_names(columns)
    for flight in flights: 
        print(" | ".join(f"{column_names[i]}: {flight[i]}" for i in range(len(columns))))
        print("-" * 50)
    return flights

# helper funtion to format the column names passed into, or defined in, 'display_flights' to enable the column names to be dynamically
# formatted so they can be displayed in a readable format
def format_column_names(columns):
    formatted_names = []
    for column in columns:
        # use alias for column name if present
        if " AS " in column.upper():
            name = column.split(" AS ")[-1]
        # remove table alias if present
        elif "." in column:
            name = column.split(".")[-1]
        else:
            name = column
        # special case to display city and country as destinations
        if 'city' in name.lower(): 
            name = "Destination City"
        if 'country' in name.lower():
            name = "Destination Country"

        # remove underscores from column names and capitalise
        name = name.replace("_", " ").title()
        # capitalise 'id'
        name = name.replace(" Id", " ID")
        formatted_names.append(name)
    return formatted_names
