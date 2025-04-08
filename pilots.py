import sqlite3
from flights_helpers import display_flights, get_flight
from menu import clear_console, create_menu
from pilots_helpers import confirm_pilot_update, get_current_pilot, get_license_number, get_name, select_pilot



def display_pilots_menu(previous_menu):
    def return_to_pilots_menu():
        return_to_pilots_menu(previous_menu)
    pilots_menu = {
        "heading": "=== Pilot Scheduling & Information Menu ===",
    "1": ("Assign a pilot to a flight", assign_pilot_to_flight),
    "2": ("View a pilot's schdule", view_assigned_flights),
    "3": ("Add a new pilot to the system", add_pilot),
    "4": ("Delete a pilot from the system", delete_pilot),
    "5": ("Update a pilot's details", lambda: update_details_menu(return_to_pilots_menu)),
    "6": ("View the number of pilots that have flown to a given destination", view_pilots_for_destination),
    "7": ("Return to Previous Menu", lambda: create_menu(previous_menu)),
}
    create_menu(pilots_menu, previous_menu)

# function to assign a pilot to a flight. Calls 'get_flight' to retrive a valid flight from the user, ensuring
# pilots cannot be assigned to past or cancelled flights. Calls 'get_current_pilot' and, if a pilot is already 
# assigned to the flight, calls confirm_pilot_update to prompt hte user to conofim they wish to replace the 
# currently assigned pilot with a new one. Calls 'select_pilot' to retrive a pilot to assign from the user. 
# Updates the database and prints a success message to the user. 
def assign_pilot_to_flight():
    flight_to_update = get_flight("assign a pilot to", columns=["flight_id", "flight_number", "pilot_id", "departure_time", "arrival_time"], exclude_status="cancelled", is_future=True)
    flight_id, flight_number, departure_time, arrival_time = flight_to_update[0], flight_to_update[1], flight_to_update[3], flight_to_update[4]
    current_pilot_id, current_pilot_name = get_current_pilot(flight_to_update)
    if current_pilot_id:
        update_assigned_pilot = confirm_pilot_update(current_pilot_name, current_pilot_id, flight_number)  
        if not update_assigned_pilot:
            return      
    pilot_id, pilot_name = select_pilot(departure_time, arrival_time, flight_number, only_available=True)
    conn = sqlite3.connect('flight_management')
    conn.execute("UPDATE flights SET pilot_id = ? WHERE flight_id = ?", (pilot_id, flight_id) )
    conn.commit()
    conn.close()
    clear_console()
    print(f"Pilot {pilot_name} has been assigned to flight {flight_number}.\n")

def view_schedule():
    print("x")

# function to view a pilot's schedule. Calls 'select pilot' to display a list of pilots for the user to 
# choose from and return a pilot_id and pilot_name. Passes the relavent columns and pilot_id to display all
# flights assigned to that pilot. 
def view_assigned_flights():
    clear_console()
    pilot_id, pilot_name = select_pilot(action="view assigned flights for: ")
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
    display_flights(columns, pilot=pilot_id)

# function to add a new pilot to the Flight Management System. Calls helper functions to receive a 
# valid name and license number from the user, then queries the database to check a pilot with the 
# provided license number does not already exist. If the licesnse number is unique, the pilot's details
# are added to the database and a success message is displayed. If the license number already exists, the
# pilot cannot be added (license numbers must be unique), so a relavent message is diaplyeed before returning to 
# the 'Pilot Scheduling & Information Menu'  
def add_pilot():
    clear_console()
    print("========== Add a pilot to the Flight Management System ==========\n")
    first_name, last_name = get_name()
    license_number = get_license_number(f"{first_name} {last_name}")  
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pilots WHERE license_number = ?", (license_number,))
    if cursor.fetchone():
        print(f"\nPilot with license number {license_number} already exists. Unable to add {first_name} {last_name} to the Flight Management System.")
        conn.close()
        return
    cursor.execute(
        "INSERT INTO pilots (first_name, last_name, license_number) VALUES (?, ?, ?)",
        (first_name, last_name, license_number)
    )
    conn.commit()
    print(f"\nPilot {first_name} {last_name} with license {license_number} has been added successfully.")

# function to delete a pilot from the Flight Management System. Calls 'select pilot' to display a list of pilots for the user to 
# choose from and return a pilot_id and pilot_name. Calls 'display_flights' to print any scheduled flights assigned to 
# the selected pilot, then prompts the user to confirm that they wish to delete the pilot from the system. If the user chooses 
# not to delete the pilot, a relavant message is displayed, before returnig to the 'Pilot Scheduling & Information Menu'. If the
# user chooses to delete the pilot, the flights table is queried to update any flights with the chosen pilot_id to NULL (preventing
# foreign key issues), then the pilot is deleted from the pilots table and a success message is displayed. 
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
    def return_to_pilots_menu():
        display_pilots_menu(previous_menu)
    update_details_menu = {
        "heading": "=== Update a pilot's details ===",
    "1": ("Update the pilot's name", lambda: update_details("name", return_to_pilots_menu)),
    "2": ("Update the pilot's license number", lambda: update_details("license number", return_to_pilots_menu)),
    "3": ("Cancel", lambda: previous_menu()),
    }
    clear_console()
    create_menu(update_details_menu, previous_menu)

# function to update a pilot's name or license number. Calls 'select pilot' to display a list of pilots for the user to 
# choose from and return a pilot_id and pilot_name. Calls the relavent helper function dependent on the field passed 
# to recieve a valid name or license number from the user. When the license number is being updated, the database is queried 
# to check a pilot with the provided license number does not already exist. If the license number already exists, the
# pilot cannot be added (license numbers must be unique), so a relavent message is displayed before returning to 
# the 'Update a pilot's details' menu. The pilots table is updated then queried to retrieve the full details, which are displayed 
# in a success message. 
def update_details(field, return_to_pilots_menu):
    print(f"========== Update a pilot's {field} ==========\n")
    pilot_id, pilot_name = select_pilot(action="update details for")
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    clear_console()
    if field == "name":
        first_name, last_name = get_name()
        cursor.execute("UPDATE pilots SET first_name = ?, last_name = ? WHERE pilot_id = ?", (first_name, last_name, pilot_id)) 
    if field == "license number":
        license_number = get_license_number(pilot_name)
        cursor.execute("SELECT * FROM pilots WHERE license_number = ?", (license_number,))
        if cursor.fetchone():
            print(f"\nPilot with license number {license_number} already exists. Unable to update {pilot_name}'s license number.")
            conn.close()
            return
        cursor.execute("UPDATE pilots SET license_number = ? WHERE pilot_id = ?", (license_number, pilot_id)) 
    conn.commit()
    cursor.execute("SELECT first_name, last_name, license_number FROM pilots WHERE pilot_id = ?", (pilot_id,))
    pilot_details = cursor.fetchone()
    conn.close()
    if pilot_details:
        first_name, last_name, license_number = pilot_details
        print(f"\nPilot details updated: Name - {first_name} {last_name}, License Number - {license_number}.")
    else:
        print(f"\nError: Pilot with ID {pilot_id} not found.")
    input("\nPress Enter to return to the Pilot Scheduling & Information Menu")
    return_to_pilots_menu()

def view_pilots_for_destination():
    print("x")

