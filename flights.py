from datetime import datetime
from menu import clear_console, create_menu
import sqlite3
date_format = "%Y-%m-%d %H:%M:%S"
# function to display the top-level 'flights' menu - 'Flight Management' menu and handle user 
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
    create_menu(flights_menu, previous_menu)
  
# function to display the 'Update a Flight' menu and handle user 
# selection. Accepts the previous_menu to allow the user to return to the 'Flight 
# Management' menu. Calls 'create_menu' to print the menu and handle user input. 
def update_flights_menu(previous_menu):
    update_flights_menu = {
        "heading": "=== Update a Flight Menu ===",
    "1": ("Change departure time", change_departure_time),
    
    "3": ("Change flight status", cancel_a_flight), # including cancel
    "5": ("Assign or updated assigned pilot", assign_update_pilot),
    "6": ("Update flight destination", update_flight_destination),
}
    create_menu(update_flights_menu, previous_menu)

def is_valid_datetime(date_string, date_format="%Y-%m-%d %H:%M:%S"):
    try:
        # Try to parse the date string into a datetime object using the provided format
        datetime.strptime(date_string, date_format)
        return True  # If parsing is successful, it's a valid format
    except ValueError:
        return False  # If there's a ValueError, the format is incorrect
    
# function to update the departure time of a flight. Calls 'display_flights' with a list of
# relavent columns to display and 'is_future' set to true to display only upcoming flights. 
# Asks the user to input the ID of the flight they want to update then checks it's a valid
# flight_id. Asks the user to enter the new date and time for the flight and checks the
# date is formatted correctly and not in the past. Find the durtaion of the flight then 
# updates both the departure and arrival time accoredingly. Displays a success message to 
# the user.
def change_departure_time():
    clear_console()
    while True:
        print("==========Upcoming Flights==========\n")
        flights = display_flights(columns=["flight_id", "flight_number", "departure_time", "arrival_time"], is_future=True)
        flight_id = input("\nPlease enter the flight_id of the flight you'd like to update: ")
        try: flight_id = int(flight_id)
        except ValueError:
            print("\nInvalid input. Please enter a valid flight ID.")
            continue
        flight_to_update = next((flight for flight in flights if flight[0] == flight_id), None)

        if flight_to_update:
            while True:
                new_departure_time = input("\nPlease enter a new departure time (YYYY-MM-DD HH:MM:SS): ")
                try: new_departure_time = datetime.strptime(new_departure_time, date_format)
                except ValueError:
                    print("\nInvalid departure time format. Please use the format 'YYYY-MM-DD HH:MM:SS'.")
                    continue
                if new_departure_time <= datetime.now():
                    print("\nInvalid input. The provided departure time must be in the future.")
                    continue
                break
            
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
            break
        else:
            clear_console() 
            print(str(flight_id) + "\nInvalid choice, please try again.\n")





def cancel_a_flight():
    clear_console()
    while True:
        print("==========Flights==========\n")
        flights = display_flights(columns=["flight_id", "flight_number", "status"])
        flight_id = input("\nPlease enter the flight_id of the flight you'd like to cancel: ")
        try: flight_id = int(flight_id)
        except ValueError:
            print("\nInvalid input. Please enter a valid flight ID.")
            continue
        flight_to_update = next((flight for flight in flights if flight[0] == flight_id), None)

        if flight_to_update:
            while True:
                flight_number = flight_to_update[1]
                confirmation = input(f"\nPlease confirm that you wish to cancel flight {flight_number} (y/n):")
                if confirmation.lower() == "n":
                    print("Cancellation cancelled")
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
            break
        else:
            clear_console() 
            print(str(flight_id) + "\nInvalid choice, please try again.\n")


def assign_update_pilot():
    print("x")

def update_flight_destination():
    print("x")
    


def schedule_a_flight():
    print("schedule flight")

def view_flights_menu(previous_menu):
    view_flights_menu = {
        "heading": "=== View Flights by Criteria Menu ===",
    "1": ("View flights assigned to a pilot", view_assigned_flights), # may be able to call function in pilots
    "2": ("View flights to a specific destination", view_flights_to_destination),
    "3": ("View all cancelled flights", view_cancelled_flights), # including cancel
    "4": ("Sort flights by duration", sort_flights_by_duration),
    "5": ("Search flights by departure date", search_by_departure_date),
    "6": ("Return to Previous Menu", lambda: previous_menu()),

}
    create_menu(view_flights_menu, previous_menu)

def view_assigned_flights():
    print("x")

def view_flights_to_destination():
    print("x")

def view_cancelled_flights():
    print("x")

def sort_flights_by_duration():
    print("x")

def search_by_departure_date():
    print("x")

# prints a list of all future flights
def display_flights(columns=None, pilot=None, is_future=None, departure_date=None, status=None):
    conn = sqlite3.connect('flight_management')
    
    if not columns:
        columns = ["flight_id", "flight_number", "departure_airport_id", "arrival_airport_id", "pilot_id", "departure_time", "arrival_time", "status"]
    
    columns_str = ", ".join(columns)
    query = f"SELECT {columns_str} FROM flights"
    params=[]

    if is_future:
        query += " WHERE departure_time >= CURRENT_TIMESTAMP"

    if departure_date:
        query += " WHERE DATE(departure_time) = ?"
        params.append(departure_date)

    if pilot:
        query += " AND pilot_id = ?"
        params.append(pilot)

    if status:
        query += "AND status = ?"
        params.append(status)
    
    flights = conn.execute(query, params).fetchall()
    conn.close

    if not flights: 
        print("\nNo matching flights found.")
        return None
    
    for flight in flights: 
        print(", ".join(f"{column}: {flight[i]}" for i, column in enumerate (columns)))
    
    return flights


    
    
    