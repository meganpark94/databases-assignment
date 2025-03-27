import sqlite3
conn = sqlite3.connect('flight_management')
conn.execute("PRAGMA foreign_keys = ON")


conn.execute('''CREATE TABLE IF NOT EXISTS pilots (
    pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    license_number VARCHAR(20) UNIQUE NOT NULL
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS destinations (
    destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    UNIQUE (city, country)
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS airports (
    airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_name VARCHAR(100) NOT NULL,
    iata_code VARCHAR(10) UNIQUE NOT NULL,
    destination_id INT NOT NULL,           
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id)
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number VARCHAR(50) NOT NULL,
    departure_airport_id INTEGER,  
    arrival_airport_id INTEGER,   
    pilot_id INTEGER,     
    departure_time DATETIME,
    arrival_time DATETIME,
    status VARCHAR(10) CHECK (status IN ('scheduled', 'cancelled', 'departed', 'arrived', 'delayed')),
    FOREIGN KEY (departure_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (arrival_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id)
)''')


