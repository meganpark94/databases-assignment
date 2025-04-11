import sqlite3
from destinations_helpers import add_destination, get_airport_details, get_destination
from menu import clear_console, create_menu

# function to display the top-level 'destinations' menu - 'Destination Management Menu' - and handle user 
# selection. Accepts the previous_menu to allow the user to return to the main menu. Calls 'create_menu' 
# to print the menu and handle user input
def display_destinations_menu(previous_menu):
    destinations_menu = {
    "heading": "=== Destination Management Menu ===",
    "1": ("Add an airport to the Flight Management System", add_airport),
    "2": ("Add a destination (city & country) to the Flight Management System", add_destination),
    "3": ("View the number of airports in each country", display_country_airport_count),
    "4": ("View the total number of flights from each airport", lambda: display_airport_flight_count("arriving")),
    "5": ("View the total number of flights to each airport", lambda: display_airport_flight_count("departing")),  
    "6": ("Return to Previous Menu", lambda: create_menu(previous_menu))
    }
    create_menu(destinations_menu, previous_menu)

# function to display the total number of departing or arriving flights from or to an airport. Accepts the
# 'type' of flight as an argument(departing or arriving) then sets the 'airport_id_type' accordingly. Fetches the
# number of flights to or from each airport and displays the results in a readable format
def display_airport_flight_count(type):
    clear_console()
    if type not in ("arriving", "departing"):
        raise ValueError("Type of flight must be 'arriving' or 'departing'")
    airport_id_type = "arrival_airport_id" if type == "arriving" else "departure_airport_id"
    if type == "arriving":
        print("========== View the number of flights to each airport ==========")   
    elif type == "departing":
        print("========== View the number of flights from each airport ==========") 
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT a.airport_name, a.iata_code, COUNT(f.{airport_id_type}) AS flight_count
        FROM airports a
        LEFT JOIN flights f ON a.airport_id = f.{airport_id_type}
        GROUP BY a.airport_id
        ORDER BY flight_count DESC
    ''')
    result = cursor.fetchall()
    if not result:
        print("\nNo flights found.")
        return None
    for airport_name, iata_code, flight_count in result:
        print(f"Airport: {airport_name} ({iata_code}) | Total {type} flights: {flight_count}")
        print("-" * 50)

# function to add a new airport to the Flight Management System. Calls 'get_destination' to retrieve a
# valid destination from the user, then calls 'get_airport_details' to retrieve a valid airport_name and 
# IATA code for the new airport from the user. Checks that an airport with the provided IATA code does not already
# exist - if it does, prints a message to inform the user that a duplicate IATA code cannot be used and returns.
# Otherwise, inserts the airport details into the database and displays a success message
def add_airport():
    clear_console()
    print("========== Add an airport to the Flight Management System ===========")
    chosen_destination = get_destination()
    destination_id = chosen_destination[0]
    airport_name, iata_code = get_airport_details()
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM airports WHERE iata_code = ?", (iata_code,))
    if cursor.fetchone():
        print(f"\nAn airport with IATA code '{iata_code}' already exists. Unable to add a duplicate entry to the Flight Management System.")
        conn.close()
        return
    cursor.execute("INSERT INTO airports (airport_name, iata_code, destination_id) VALUES (?, ?, ?)",(airport_name, iata_code, destination_id))
    conn.commit()
    conn.close() 
    print(f"Airport '{airport_name}' ({iata_code}) added successfully.")

# function to fetch and display the number of airports in each country in a readable format
def display_country_airport_count():
    clear_console()
    print("========== View the number of airports in each country ==========")
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.country, COUNT(a.airport_id) AS airport_count
        FROM destinations d
        LEFT JOIN airports a ON d.destination_id = a.destination_id
        GROUP BY d.country
        ORDER BY airport_count DESC
    ''')
    result = cursor.fetchall()
    if not result:
        print("\nNo cities found.")
        return None
    for country, airport_count in result:
        print(f"Country: {country} | Number of airports: {airport_count}")
        print("-" * 50)


