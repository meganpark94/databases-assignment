
def display_destinations_menu():
    destinations_menu = {
        "heading": "=== Destination Management Menu ===",
    "1": ("Add a destination to the system", add_destination), #call add airport 
    "2": ("Delete an airport from the system", delete_airport), # include warning that the destination will also be deleted if no other airports exist there
    "3": ("View the number of flights to each destination", view_flights_per_destination), # and airport
    "4": ("Add an airport to an existing destination", add_airport),
    "5": ("View the airport with the most delayed flights", view_most_delayed_flights),
    "6": ("Sort airports by the number of cancelled departing flights", view_pilots_for_destination),
    "7": ("Return to Previous Menu", lambda: create_menu(main_menu))
}
        