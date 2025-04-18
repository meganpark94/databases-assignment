import sqlite3
from menu import clear_console

# helper function to prompt the user to confirm that they wish to assign a pilot to a flight
# when the flight already has a pilot assigned.
def confirm_pilot_update(current_pilot_name, current_pilot_id, flight_number):
    clear_console()
    while True:
        print(f"\nPilot {current_pilot_name} (ID: {current_pilot_id}) is currently assigned to flight {flight_number}.")
        choice = input("\nDo you want to update the assigned pilot? (y/n): ")
        if choice.lower() == "n":
            clear_console()
            print("\nUpdate pilot assignement aborted.")
            return False
        if choice.lower() == "y":
            clear_console()
            return True
        clear_console()
        print("Your input: " + choice)
        print("\nInvalid choice, please enter 'y' or 'n' to indicate your choice.")


# helper function to retrive a pilot from the user. Calls 'display_pilots' with the provided arguments
# to ensure only the relevant piolots are displayed. Ensures the pilot_id exists and meets the criteria before
# returning the pilot id and name
def select_pilot(only_available=None, departure_time=None, arrival_time=None, flight_number=None, action=None):
    if departure_time:
        header = "==========All Pilots=========="
    else:
        header = "==========All Pilots=========="
    clear_console()
    print(header)
    pilots = display_pilots(only_available, departure_time, arrival_time)
    while True:
        if departure_time:
            pilot_id = input(f"\nPlease enter the pilot_id of the pilot you'd like to assign to flight {flight_number}: ")
        if action:
            pilot_id = input(f"\nPlease enter the pilot_id of the pilot you'd like to {action}: ")
        try: 
            pilot_id = int(pilot_id)
        except ValueError:
            clear_console()
            print(header)
            pilots = display_pilots(only_available, departure_time, arrival_time)
            print(f"\nYour input: {pilot_id}\nInvalid input. Please enter a valid pilot ID.")
            continue
        pilot_to_assign = next((pilot for pilot in pilots if pilot[0] == pilot_id), None)
        if pilot_to_assign:
            return pilot_id, f"{pilot_to_assign[1]} { pilot_to_assign[2]}"
        else: 
            clear_console()
            print(header)
            pilots = display_pilots(only_available, departure_time, arrival_time)
            print(f"\nYour input: {str(pilot_id)}\nInvalid pilot ID, please try again.")


# helper function to retrieve the pilot assigned to a specific flight. Returns the id and name of the 
# pilot currently assigned to a flight. If no pilot is yet assigned, returns None
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


# helper function to display a list of all pilots. Accepts arguments to make the function resuable.
# When 'only_available' is True, only displays pilots who are not already assigned to a flight at the time
def display_pilots(only_available=None, departure_time=None, arrival_time=None):
    conn = sqlite3.connect('flight_management')
    query = "SELECT pilot_id, first_name, last_name FROM pilots "
    params = ()
    if only_available:
        query += ''' 
            WHERE pilot_id NOT IN (
            SELECT DISTINCT pilot_id FROM flights 
            WHERE pilot_id IS NOT NULL AND (
            (departure_time <= ? AND arrival_time >= ?) 
            OR
            (departure_time <= ? AND arrival_time >= ?) 
            OR
            (departure_time >= ? AND arrival_time <= ?)  
            )
            )
        '''
        params = (departure_time, departure_time, arrival_time, arrival_time, departure_time, arrival_time)
    pilots = conn.execute(query, params).fetchall()
    conn.close()
    if not pilots: 
        print("\nNo matching pilots found.")
        return None
    for pilot_id, first_name, last_name in pilots: 
         print(f"ID: {pilot_id} | Name: {first_name} {last_name}")
    return pilots

# helper function to get the name of a pilot from the user. Used to add a pilot to the system and to update a pilot's name. 
# Ensures the provided first_name and last_name are each less than or equal to 30 characters and not empty strings
def get_name():
    while True:
        first_name = input("Please enter the pilot's first name: ").strip()
        last_name = input("Please enter the pilot's surname: ").strip()
        if len(first_name) > 30 or len(last_name) > 30: 
            clear_console()
            print(f"Your input: First name - {first_name} Surname - {last_name}\nPilot's first name and last name must not exceed 30 characters each.")
        elif not first_name or not last_name:
            clear_console()
            print(f"Your input: First name - {first_name} Surname - {last_name}\nYou must provide a value for the pilot's first name and surname.")
        else: 
            clear_console()
            return first_name, last_name  

# helper function to get the licence number of a pilot from the user. Used to add a pilot to the system and to update a pilot's licence number. 
# Ensures the provided licence number is less than or equal to 20 characters, not an empty string and does not already exist
# in the 'pilots' table
def get_licence_number(pilot_name):
    while True:
        licence_number = input(f"Please enter {pilot_name}'s licence number (e.g. LIC667788): ").strip()
        if len(licence_number) > 20: 
            clear_console()
            print(f"Your input: {licence_number} \n Pilot's licence number must not exceed 20 characters.")
        elif not licence_number:
            clear_console()
            print(f"Your input: {licence_number} \n You must provide a licence number for the pilot.")
        else: 
            clear_console()
            return licence_number