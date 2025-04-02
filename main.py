from database_queries import update_flight_status
from destinations import display_destinations_menu
from flights import display_flights_menu
from pilots import display_pilots_menu
from menu import clear_console, create_menu

main_menu = {
     "heading": "=== Main Menu ===",
    "1": ("Flight Management", lambda: display_flights_menu(main_menu)),
    "2": ("Pilot Scheduling & Information", lambda: display_pilots_menu(main_menu)),
    "3": ("Destination Management", lambda: display_destinations_menu(main_menu)),
    "4": ("Exit", lambda: (clear_console(), print("Exiting..."), exit()))
}

create_menu(main_menu)
update_flight_status()
