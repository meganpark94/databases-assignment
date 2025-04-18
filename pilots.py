import sqlite3
from flights_helpers import display_flights, get_flight
from menu import clear_console, create_menu
from pilots_helpers import confirm_pilot_update, get_current_pilot, get_licence_number, get_name, select_pilot

# function to display the top-level 'pilots' menu - 'Pilot Scheduling & Information Menu' - and handle user 
# selection. Accepts the previous_menu to allow the user to return to the main
# menu. Defines a nested function `return_to_pilots_menu` that redisplays the
# 'Pilot Scheduling & Information Menu. Calls 'create_menu' to print the menu and handle 
# user input
def display_pilots_menu(previous_menu):
    def return_to_pilots_menu():
        display_pilots_menu(previous_menu)
    pilots_menu = {
        "heading": "=== Pilot Scheduling & Information Menu ===",
        "1": ("Assign a pilot to a flight", assign_pilot_to_flight),
        "2": ("View a pilot's schdule", view_assigned_flights),
        "3": ("Add a new pilot to the system", add_pilot),
        "4": ("Delete a pilot from the system", delete_pilot),
        "5": ("Update a pilot's details", lambda: update_details_menu(return_to_pilots_menu)),
        "6": ("Return to Previous Menu", lambda: create_menu(previous_menu)),
    }
    create_menu(pilots_menu, previous_menu)

# function to assign a pilot to a flight. Calls 'get_flight' to retrive a valid flight from the user, ensuring
# pilots cannot be assigned to past or cancelled flights. Calls 'get_current_pilot' and, if a pilot is already 
# assigned to the flight, calls 'confirm_pilot_update' to prompt the user to confirm they wish to replace the 
# currently assigned pilot with a new one. Calls 'select_pilot' to retrive a pilot to assign from the user. 
# Updates the database and prints a success message to the user
def assign_pilot_to_flight():
    columns=["flight_id", "flight_number", "pilot_id", "departure_time", "arrival_time"]
    flight_to_update = get_flight("assign a pilot to", deparature_time_index=3, arrival_time_index=4, columns=columns, exclude_status="cancelled", is_future=True)
    flight_id, flight_number, departure_time, arrival_time = flight_to_update[0], flight_to_update[1], flight_to_update[3], flight_to_update[4]
    current_pilot_id, current_pilot_name = get_current_pilot(flight_to_update)
    if current_pilot_id:
        update_assigned_pilot = confirm_pilot_update(current_pilot_name, current_pilot_id, flight_number)  
        if not update_assigned_pilot:
            return      
    pilot_id, pilot_name = select_pilot(only_available=True, departure_time=departure_time, arrival_time=arrival_time, flight_number=flight_number)
    conn = sqlite3.connect('flight_management')
    conn.execute("UPDATE flights SET pilot_id = ? WHERE flight_id = ?", (pilot_id, flight_id) )
    conn.commit()
    conn.close()
    clear_console()
    print(f"Pilot {pilot_name} has been assigned to flight {flight_number}.")

# function to view a pilot's schedule. Calls 'select pilot' to display a list of pilots for the user to 
# choose from and return a pilot_id and pilot_name. Passes the relevant departure and arrival time column indicies 
# (to format time columns to be easily readable), columns and pilot_id to 'display_flights' to display all flights assigned to that pilot
def view_assigned_flights():
    clear_console()
    pilot_id, pilot_name = select_pilot(action="view assigned flights for")
    clear_console()
    print(f"========== Flights assigned to {pilot_name} ==========\n")
    columns = [
        "f.flight_number",
        "departure_airport.airport_name AS departure_airport",
        "f.departure_time",
        "arrival_airport.airport_name AS arrival_airport",
        "f.arrival_time",
        "f.status"
    ]
    display_flights(departure_time_index=2, arrival_time_index=4, columns=columns, pilot=pilot_id)

# function to add a new pilot to the Flight Management System. Calls helper functions to receive a 
# valid name and licence number from the user, then queries the database to check a pilot with the 
# provided licence number does not already exist. If the licesnse number is unique, the pilot's details
# are added to the database and a success message is displayed. If the licence number already exists, the
# pilot cannot be added (licence numbers must be unique), so a relevant message is displayed before returning to 
# the 'Pilot Scheduling & Information Menu'  
def add_pilot():
    clear_console()
    print("========== Add a pilot to the Flight Management System ==========\n")
    first_name, last_name = get_name()
    licence_number = get_licence_number(f"{first_name} {last_name}")  
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pilots WHERE licence_number = ?", (licence_number,))
    if cursor.fetchone():
        print(f"\nPilot with licence number {licence_number} already exists. Unable to add {first_name} {last_name} to the Flight Management System.")
        conn.close()
        return
    cursor.execute("INSERT INTO pilots (first_name, last_name, licence_number) VALUES (?, ?, ?)", (first_name, last_name, licence_number))
    conn.commit()
    print(f"\nPilot {first_name} {last_name} with licence {licence_number} has been added successfully.")

# function to delete a pilot from the Flight Management System. Calls 'select_pilot' to display a list of pilots for the user to 
# choose from and return a pilot_id and pilot_name. Calls 'display_flights' to print any scheduled flights assigned to 
# the selected pilot, then prompts the user to confirm that they wish to delete the pilot from the system. If the user chooses 
# not to delete the pilot, a relevant message is displayed, before returnig to the 'Pilot Scheduling & Information Menu'. If the
# user chooses to delete the pilot, the flights table is queried to update any flights with the chosen pilot_id to NULL (preventing
# foreign key constraint violations), then the pilot is deleted from the pilots table and a success message is displayed
def delete_pilot():
    clear_console()
    print("========== Delete a pilot from the Flight Management System ==========\n")
    pilot_id, pilot_name = select_pilot(action="delete from the Flight Management System")
    clear_console()
    flights = display_flights(pilot=pilot_id, is_future=True, exclude_status="cancelled")
    if flights and len(flights) > 0:
         print(f"\nPilot {pilot_name} is assigned to the above scheduled flights.")
    else: clear_console()
    while True:    
        choice = input(f"\nAre you sure you want to delete {pilot_name} from the Flight Management System? (y/n): ")
        if choice.lower() == "n":
            clear_console()
            print("\nDelete pilot aborted.")
            return
        if choice.lower() == "y":
            clear_console()
            break
        clear_console()
        print(f"Your input: {choice}\nInvalid choice, please enter 'y' or 'n' to indicate your choice.")
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("UPDATE flights SET pilot_id = NULL WHERE pilot_id = ?", (pilot_id,))        
    cursor.execute("DELETE FROM pilots WHERE pilot_id = ?", (pilot_id,))
    conn.commit()
    conn.close()
    print(f"\nPilot {pilot_name} has been deleted from the Flight Management System and unassigned from all flights.")

# function to display the 'Update a pilot's details' menu and handle user 
# selection. Accepts the previous_menu to allow the user to return to the 'Pilot Scheduling & Information Menu'. 
# Calls 'create_menu' to print the menu and handle user input. 
def update_details_menu(previous_menu):
    update_details_menu = {
        "heading": "=== Update a pilot's details ===",
        "1": ("Update the pilot's name", lambda: update_details("name", previous_menu)),
        "2": ("Update the pilot's licence number", lambda: update_details("licence number", previous_menu)),
        "3": ("Cancel", lambda: previous_menu()),
    }
    clear_console()
    create_menu(update_details_menu, previous_menu)

# function to update a pilot's name or licence number. Calls 'select pilot' to display a list of pilots for the user to 
# choose from and return a pilot_id and pilot_name. Calls the relevant helper function dependent on the field passed 
# to receive a valid name or licence number from the user. When the licence number is being updated, the database is queried 
# to check a pilot with the provided licence number does not already exist. If the licence number already exists, the
# pilot cannot be added (licence numbers must be unique), so a relevant message is displayed before returning to 
# the 'Update a pilot's details' menu. The pilots table is updated then queried to retrieve the full details, which are displayed 
# in a success message
def update_details(field, return_to_pilots_menu):
    print(f"========== Update a pilot's {field} ==========\n")
    pilot_id, pilot_name = select_pilot(action="update details for")
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    clear_console()
    if field == "name":
        first_name, last_name = get_name()
        cursor.execute("UPDATE pilots SET first_name = ?, last_name = ? WHERE pilot_id = ?", (first_name, last_name, pilot_id)) 
    if field == "licence number":
        licence_number = get_licence_number(pilot_name)
        cursor.execute("SELECT * FROM pilots WHERE licence_number = ?", (licence_number,))
        if cursor.fetchone():
            print(f"\nPilot with licence number {licence_number} already exists. Unable to update {pilot_name}'s licence number.")
            conn.close()
            return
        cursor.execute("UPDATE pilots SET licence_number = ? WHERE pilot_id = ?", (licence_number, pilot_id)) 
    conn.commit()
    cursor.execute("SELECT first_name, last_name, licence_number FROM pilots WHERE pilot_id = ?", (pilot_id,))
    pilot_details = cursor.fetchone()
    conn.close()
    if pilot_details:
        first_name, last_name, licence_number = pilot_details
        print(f"\nPilot details updated: Name - {first_name} {last_name}, licence Number - {licence_number}.")
    else:
        print(f"\nError: Pilot with ID {pilot_id} not found.")
    input("\nPress Enter to return to the Pilot Scheduling & Information Menu")
    return_to_pilots_menu()


