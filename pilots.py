import sqlite3
from menu import create_menu



def display_pilots_menu(previous_menu):
    pilots_menu = {
        "heading": "=== Pilot Scheduling & Information Menu ===",
    "1": ("Assign a pilot to a flight", assign_pilot_to_flight),
    "2": ("View a pilot's schdule", view_schedule),
    "3": ("View the flights assigned to a pilot", view_assigned_flights),
    "4": ("Add a new pilot to the system", add_pilot),
    "5": ("Delete a pilot from the system", delete_pilot),
    "6": ("Update a pilot's details", update_details),
    "7": ("View the number of pilots that have flown to a given destination", view_pilots_for_destination),
    "4": ("Return to Previous Menu", lambda: previous_menu()),
}
    create_menu(pilots_menu, previous_menu)

def assign_pilot_to_flight():
    print("x")

def view_schedule():
    print("x")

def view_assigned_flights():
    print("x")

def add_pilot():
    print("x")

def delete_pilot():
    print("x")

def update_details():
    print("x")

def view_pilots_for_destination():
    print("x")



def display_pilots(only_available=None, departure_time=None, arrival_time=None):
    conn = sqlite3.connect('flight_management')
    query = "SELECT pilot_id, first_name, last_name FROM pilots"
    if only_available:
        query += ''' WHERE pilot_id NOT IN (
            SELECT pilot_id FROM flights 
            WHERE (
            (departure_time <= ? AND arrival_time >= ?)  -- Overlapping departure
            OR
            (departure_time <= ? AND arrival_time >= ?)  -- Overlapping arrival
            OR
            (departure_time >= ? AND arrival_time <= ?)  -- Fully inside another flight
            )
            )'''
        params = (departure_time, departure_time, arrival_time, arrival_time, departure_time, arrival_time)
    else:
        params = ()

    pilots = conn.execute(query, params).fetchall()
    conn.close

    if not pilots: 
        print("\nNo matching pilots found.")
        return None
    
    for pilot_id, first_name, last_name in pilots: 
         print(f"ID: {pilot_id} | Name: {first_name} {last_name}")
    
    return pilots