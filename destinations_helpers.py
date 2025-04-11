import sqlite3
from menu import clear_console

# helper function to fetch the details of a destination. Calls 'display_destinations' then asks the user to input 
# the ID of the desination they want to select, or to press 'Enter' to add a new destination. On 'Enter', calls 'add_destination'
# to retrive a valid destination (unique city and country combination) from the user then returns the destination details and displays a success message.
# Otherwise, ensures the user has chosen a valid destination, then returns the destination details as a tuple and displays a success message.
def get_destination():
    destinations = display_destinations()
    while True:
        response = input("Each airport must be linked to a destination. Enter an exising destination ID from the list above, or press 'Enter' to add a new destination: ")
        if response.strip() == "":
            conn = sqlite3.connect('flight_management')
            cursor = conn.cursor()
            city, country = add_destination()
            response = cursor.execute("SELECT destination_id FROM destinations WHERE city = ? and country = ?", (city, country)).fetchone()[0]
            conn.close()
            if response:
                print(f"Destination selected: {city} ({country})")
            return response, city, country
        try: destination_id = int(response)
        except ValueError:
            clear_console()
            destinations = display_destinations()
            print("Your input: " + str(response) + "\nInvalid input. Please enter a valid destination ID or press 'Enter' to add a new destination.\n")
            continue
        chosen_destination = next((destination for destination in destinations if destination[0] == destination_id), None)
        if chosen_destination:
            print(f"Destination selected: {chosen_destination[1]} ({chosen_destination[2]})")
            return chosen_destination
        else: 
            clear_console()
            destinations = display_destinations()
            print(f"Your input:{response}\nInvalid Destination ID, please try again.\n")
           

# helper function to retrieve the name and IATA code of an airport from the user. Used to add an airport to the system. 
# Ensures the provided airport_name and IATA codes are less than or equal to 100 characters and 10 characters, respectivly, and not empty strings
def get_airport_details():
    while True:
        airport_name = input("Please enter the name of the airport (e.g. Heathrow Airport): ").strip()
        iata_code = input("Please enter the IATA code (e.g. LHR): ").strip()
        if len(airport_name) > 100 or len(iata_code) > 10: 
            clear_console()
            print(f"Your input: Airport name - {airport_name} IATA code - {iata_code}\n Airport name and IATA code must be less than 100 and 10 characters, respectivly.")
        elif not airport_name or not iata_code:
            clear_console()
            print(f"Your input: Airport name - {airport_name} IATA code - {iata_code}\n You must provide a value for the airport's name and IATA code.")
        else: 
            clear_console()
            return airport_name, iata_code  

# helper function to allow the user to add a new destination to the system. Ensures the provided city and country are each less than or equal 
# to 50 characters and not empty strings. Checks that the destination provided is unique (the city/country does not already exist). If not unique, 
# displays an informative message then returnss the destination details to allow them to be used when adding an airport. Otherwise, inserts the 
# new destination into the database, displays a success message and returns the destination details. 
def add_destination():
    clear_console()
    print("========== Add a destination to the Flight Management System ==========")
    while True:
        city = input("Please enter the destination city: ").strip()
        country= input("Please enter the destination country: ").strip()
        if len(city) > 50 or len(country) > 50: 
            clear_console()
            print(f"Your input: City - {city} Country - {country}\nDestination city and country must not exceed 50 characters each.")
        elif not city or not country:
            clear_console()
            print(f"Your input: City - {city} Country - {country}\nYou must provide a value for the destination city and country.")
        else: 
           break
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT (*) FROM destinations WHERE city = ? and country = ?", (city, country))
    if cursor.fetchone()[0] > 0:
        print(f"\nThe destination {city}, {country} already exists. Unable to add a duplicate destination to the Flight Management System.")
        conn.close()
        return city, country
    cursor.execute("INSERT INTO destinations (city, country) VALUES (?, ?)", (city, country))
    conn.commit()
    conn.close()
    print(f"\nDestination {city} {country} has been added successfully.")
    return city, country

# helper function to fetch and display a list of all saved destinations
def display_destinations():
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    destinations = cursor.execute("SELECT * FROM destinations ORDER BY country, city").fetchall()
    conn.close()
    if not destinations:
        print("\nNo destinations found.")
        return None
    print("========== Destinations ==========")
    for destination_id, city, country in destinations:
        print(f"{city}, {country} (ID:{destination_id})")
        print("-" * 50)
    return destinations

# helper function to fetch and display a list of aiports and their corresponding destinations (city & country).
# Optionally accepts a departure_airport_id ehcih, when provided, will be excluded from the results - used to omit the
# departure aurport when choosing an arrival airport for a flight
def display_airports_and_destinations(departure_airport_id=None):
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()
    query = '''
        SELECT a.airport_id, a.airport_name, a.iata_code, d.city, d.country 
        FROM airports AS a
        JOIN destinations AS d ON a.destination_id = d.destination_id
    '''
    params = ()
    if departure_airport_id:
        query += " WHERE a.airport_id != ?"
        params = (departure_airport_id,)
    query += " ORDER BY d.country, d.city, a.airport_name"
    cursor.execute(query, params)
    airports = cursor.fetchall()
    conn.close()
    if not airports:
        print("\nNo airports found.")
        return None
    clear_console()
    print("==========Airports==========")
    for airport_id, airport_name, iata_code, city, country in airports:
        print(f"Airport ID: {airport_id} | Airport: {airport_name} | IATA code: {iata_code} | Destination: {city}, {country}")
        print("-" * 50)
    return airports
