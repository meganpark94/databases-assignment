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

