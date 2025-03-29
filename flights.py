from menu import create_menu

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
    "1": ("Update a flight", update_flights_menu),
    "2": ("Schedule a flight", schedule_a_flight),
    "3": ("View flights by criteria", lambda: view_flights_menu(return_to_flights_menu)),
    "4": ("Return to Previous Menu", lambda: create_menu(previous_menu)),
}
    create_menu(flights_menu, previous_menu)
  
# function to display the 'Update a Flight' menu and handle user 
# selection. Accepts the previous_menu to allow the user to return to the 'Flight 
# Management' menu. Calls 'create_menu' to print the menu and handle user input. 
def update_flights_menu():
    update_flights_menu = {
        "heading": "=== Update a Flight Menu ===",
    "1": ("Change departure time", change_departure_time),
    "2": ("Change arrival time", change_arrival_time),
    "3": ("Change flight status", change_flight_status), # including cancel
    "4": ("Change arrival time", change_arrival_time),
    "5": ("Assign or updated assigned pilot", assign_update_pilot),
    "6": ("Update flight destination", update_flight_destination),
}
    create_menu(update_flights_menu)

def change_departure_time():
    print("x")

def change_arrival_time():
    print("x")

def change_flight_status():
    print("x")

def change_arrival_time():
    print("x")

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
