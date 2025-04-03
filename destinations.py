# function to display the 
import sqlite3


def display_destinations_menu():
    destinations_menu = {
        "heading": "=== Destination Management Menu ===",
    "1": ("Add a destination to the system", add_destination), #call add airport 
    
    "3": ("View the number of flights to each destination", view_flights_per_destination), # and airport
    "4": ("Add an airport to an existing destination", add_airport),
    "5": ("View the airport with the most delayed flights", view_most_delayed_flights),
    "6": ("Sort airports by the number of cancelled departing flights", view_pilots_for_destination),
    "7": ("Return to Previous Menu", lambda: create_menu(main_menu))
}

def display_airports_and_destinations(departure_airport_id=None):
    conn = sqlite3.connect('flight_management')
    cursor = conn.cursor()

    query = """
    SELECT a.airport_id, a.airport_name, a.iata_code, d.city, d.country 
    FROM airports AS a
    JOIN destinations AS d ON a.destination_id = d.destination_id
    """
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

    print("\n==========Airports==========")
    for airport_id, airport_name, iata_code, city, country in airports:
        print(f"Airport ID: {airport_id} | Airport: {airport_name} | IATA code: {iata_code} | Destination: {city}, {country}")

    return airports
