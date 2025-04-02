import sqlite3
import time
conn = sqlite3.connect('flight_management')

# enable the enforcement of foreign key constraints in SQLite
conn.execute("PRAGMA foreign_keys = ON")

# create a pilots table where each row must not be null and the
# license number must be unique
conn.execute('''CREATE TABLE IF NOT EXISTS pilots (
    pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    license_number VARCHAR(20) UNIQUE NOT NULL
)''')

# create a destinations table where each city and counrty combination must only exist once
conn.execute('''CREATE TABLE IF NOT EXISTS destinations (
    destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    UNIQUE (city, country)
)''')

# create an airports table with a foreign key referencing the destinations table - every
# airport must be linked to a destination 
conn.execute('''CREATE TABLE IF NOT EXISTS airports (
    airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_name VARCHAR(100) NOT NULL,
    iata_code VARCHAR(10) UNIQUE NOT NULL,
    destination_id INT NOT NULL,           
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id)
)''')

# create a flights table where the status must be one of the specified options and
# the arrival time must be after the departure time. Forign key constraints used to 
# ensure the departure and arrival airport IDs and the pilot IDs reference entries in
# the airports and pilots tables, respectively.
conn.execute('''CREATE TABLE IF NOT EXISTS flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number VARCHAR(50) NOT NULL,
    departure_airport_id INTEGER,  
    arrival_airport_id INTEGER,   
    pilot_id INTEGER,     
    departure_time DATETIME,
    arrival_time DATETIME,
    status VARCHAR(10) CHECK (status IN ('scheduled', 'cancelled', 'departed')),
    FOREIGN KEY (departure_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (arrival_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (pilot_id) REFERENCES pilots(pilot_id),
    CHECK (arrival_time > departure_time)
)''')
 

# create a trigger to update the status of each new entry inserted into the flights table
# based on the flight's departure_date. If the departure_date was in the past, the flight stauts will 
# default to 'departed' and a flight with a departure_date in the future will be assigned a status
# of 'scheduled' unless the flight's status was set to cancelled. 
# conn.execute('''CREATE TRIGGER handle_flight_status_on_insert
# AFTER INSERT ON flights
# FOR EACH ROW
# BEGIN
#     UPDATE flights
#     SET status = CASE
# WHEN NEW.status = 'cancelled' THEN 'cancelled'
#                     WHEN NEW.departure_time < CURRENT_TIMESTAMP THEN 'departed'
#                     ELSE 'scheduled'
#                  END
#     WHERE flight_number = NEW.flight_number;
# END;
# ''')
# conn.commit()




# insert sample data into the destinations table

# conn.execute('''INSERT INTO destinations (city, country)
# VALUES
#     ('New York', 'USA'),  
#     ('Los Angeles', 'USA'),
#     ('London', 'UK'),
#     ('Paris', 'France'),
#     ('Tokyo', 'Japan'),
#     ('Berlin', 'Germany'),
#     ('Sydney', 'Australia'),
#     ('Rome', 'Italy'),
#     ('Toronto', 'Canada'),
#     ('Madrid', 'Spain'),
#     ('Dubai', 'UAE'),
#     ('Bangkok', 'Thailand'),
#     ('Moscow', 'Russia'),
#     ('Cairo', 'Egypt'),
#     ('Amsterdam', 'Netherlands'),
#     ('Mexico City', 'Mexico'),
#     ('Singapore', 'Singapore'),
#     ('Cape Town', 'South Africa'),
#     ('Rio de Janeiro', 'Brazil'),
#     ('Mumbai', 'India')

# # ''')
# conn.commit()

# insert sample data into the airports table
# conn.execute('''INSERT INTO airports (airport_name, iata_code, destination_id)
# VALUES
#     ('John F. Kennedy International Airport', 'JFK', 1),  -- New York
#     ('LaGuardia Airport', 'LGA', 1),  -- New York
#     ('Los Angeles International Airport', 'LAX', 2),  -- Los Angeles
#     ('San Francisco International Airport', 'SFO', 2),  -- Los Angeles
#     ('London Heathrow Airport', 'LHR', 3),  -- London
#     ('London Gatwick Airport', 'LGW', 3),  -- London
#     ('Charles de Gaulle Airport', 'CDG', 4),  -- Paris
#     ('Tokyo International Airport', 'HND', 5),  -- Tokyo
#     ('Berlin Brandenburg Airport', 'BER', 6),  -- Berlin
#     ('Sydney Kingsford Smith Airport', 'SYD', 7),  -- Sydney
#     ('Rome Fiumicino Airport', 'FCO', 8),  -- Rome
#     ('Toronto Pearson International Airport', 'YYZ', 9),  -- Toronto
#     ('Adolfo Suárez Madrid–Barajas Airport', 'MAD', 10),  -- Madrid
#     ('Dubai International Airport', 'DXB', 11),  -- Dubai
#     ('Suvarnabhumi Airport', 'BKK', 12),  -- Bangkok
#     ('Sheremetyevo International Airport', 'SVO', 13),  -- Moscow
#     ('Cairo International Airport', 'CAI', 14),  -- Cairo
#     ('Amsterdam Schiphol Airport', 'AMS', 15),  -- Amsterdam
#     ('Mexico City International Airport', 'MEX', 16),  -- Mexico City
#     ('Singapore Changi Airport', 'SIN', 17),  -- Singapore
#     ('Cape Town International Airport', 'CPT', 18),  -- Cape Town
#     ('Rio de Janeiro-Galeão International Airport', 'GIG', 19),  -- Rio de Janeiro
#     ('Chhatrapati Shivaji Maharaj International Airport', 'BOM', 20)  -- Mumbai


# ''')
# conn.commit()
# insert sample data into the pilots table
# conn.execute('''INSERT INTO pilots (first_name, last_name, license_number)
# VALUES
#     ('John', 'Doe', 'LIC123456'),
#     ('Jane', 'Smith', 'LIC987654'),
#     ('Robert', 'Johnson', 'LIC112233'),
#     ('Emily', 'Brown', 'LIC445566'),
#     ('Michael', 'Davis', 'LIC778899'),
#     ('Sarah', 'Miller', 'LIC998877'),
#     ('David', 'Wilson', 'LIC223344'),
#     ('Daniel', 'Moore', 'LIC334455'),
#     ('Olivia', 'Taylor', 'LIC556677'),
#     ('James', 'Anderson', 'LIC667788');
# ''')

# conn.commit()
# insert sample data into the flights
# conn.execute('''INSERT INTO flights (flight_number, departure_airport_id, arrival_airport_id, pilot_id, departure_time, arrival_time, status)
# VALUES
#     ('NY100', 1, 2, 1, '2025-02-01 10:00:00', '2025-02-01 13:00:00', 'scheduled'),  -- John F. Kennedy International Airport -> LaGuardia Airport (Pilot 1)
#     ('LA200', 3, 4, 2, '2025-03-02 14:00:00', '2025-03-02 17:00:00', 'scheduled'),  -- Los Angeles International Airport -> San Francisco International Airport (Pilot 2)
#     ('LD300', 5, 6, 3, '2025-03-03 09:00:00', '2025-03-03 11:30:00', 'scheduled'),  -- London Heathrow Airport -> London Gatwick Airport (Pilot 3)
#     ('TP400', 7, 8, 4, '2025-03-04 16:00:00', '2025-03-04 19:30:00', 'scheduled'),  -- Charles de Gaulle Airport -> Tokyo International Airport (Pilot 4)
#     ('BR500', 9, 10, 5, '2025-03-05 20:00:00', '2025-03-06 02:00:00', 'scheduled'),  -- Berlin Brandenburg Airport -> Sydney Kingsford Smith Airport (Pilot 5)
#     ('SY600', 11, 12, 6, '2025-03-06 08:00:00', '2025-03-06 12:00:00', 'scheduled'),  -- Rome Fiumicino Airport -> Toronto Pearson International Airport (Pilot 6)
#     ('RO700', 13, 14, 7, '2025-03-07 09:00:00', '2025-03-07 11:00:00', 'scheduled'),  -- Adolfo Suárez Madrid–Barajas Airport -> Dubai International Airport (Pilot 7)
#     ('FM800', 15, 16, 8, '2025-03-08 14:00:00', '2025-03-08 18:00:00', 'scheduled'),  -- Suvarnabhumi Airport -> Sheremetyevo International Airport (Pilot 8)
#     ('DC900', 17, 18, 9, '2025-03-09 07:00:00', '2025-03-09 10:00:00', 'scheduled'),  -- Cairo International Airport -> Amsterdam Schiphol Airport (Pilot 9)
#     ('AS1000', 19, 20, 10, '2025-03-10 16:00:00', '2025-03-10 20:00:00', 'scheduled'),  -- Mexico City International Airport -> Singapore Changi Airport (Pilot 10)
#     ('RS1100', 21, 22, 1, '2025-03-11 11:00:00', '2025-03-11 14:30:00', 'scheduled'),  -- Cape Town International Airport -> Rio de Janeiro-Galeão International Airport (Pilot 1)
#     ('MX1200', 23, 1, 2, '2025-03-12 09:30:00', '2025-03-12 13:00:00', 'scheduled'),  -- Chhatrapati Shivaji Maharaj International Airport -> John F. Kennedy International Airport (Pilot 2)
#     ('CP1300', 2, 3, 3, '2025-03-13 12:00:00', '2025-03-13 16:00:00', 'scheduled'),  -- LaGuardia Airport -> Los Angeles International Airport (Pilot 3)
#     ('NG1400', 4, 5, 4, '2025-04-14 10:00:00', '2025-04-14 13:00:00', 'scheduled'),  -- San Francisco International Airport -> London Heathrow Airport (Pilot 4)
#     ('SG1500', 6, 7, 5, '2025-04-15 14:00:00', '2025-04-15 18:30:00', 'scheduled'),  -- London Gatwick Airport -> Charles de Gaulle Airport (Pilot 5)
#     ('FM1600', 8, 9, 6, '2025-04-16 18:00:00', '2025-04-16 22:00:00', 'scheduled'),  -- Tokyo International Airport -> Berlin Brandenburg Airport (Pilot 6)
#     ('CA1700', 10, 11, 7, '2025-04-17 07:00:00', '2025-04-17 10:00:00', 'scheduled'),  -- Sydney Kingsford Smith Airport -> Rome Fiumicino Airport (Pilot 7)
#     ('BR1800', 12, 13, 8, '2025-04-18 13:00:00', '2025-04-18 17:00:00', 'scheduled'),  -- Toronto Pearson International Airport -> Adolfo Suárez Madrid–Barajas Airport (Pilot 8)
#     ('LD1900', 14, 15, 9, '2025-04-19 15:00:00', '2025-04-19 19:30:00', 'scheduled'),  -- Dubai International Airport -> Suvarnabhumi Airport (Pilot 9)
#     ('CT2000', 16, 17, 10, '2025-04-20 10:00:00', '2025-04-20 14:00:00', 'scheduled');  -- Sheremetyevo International Airport -> Cairo International Airport (Pilot 10)

# ''')


# Function to update flight status based on the current timestamp. This function 
# is called in main, therefore, each time the programme is run, the flight statuses 
# will be udated so any flights with a departure date in the past will have their status 
# changed to departed, unless the status has been explicitly set to canclled. 
def update_flight_status():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE flights
    SET status = CASE
                    WHEN status = 'cancelled' THEN 'cancelled'
                    WHEN departure_time < CURRENT_TIMESTAMP THEN 'departed'
                    ELSE 'scheduled'
                 END
    ''')
    
    conn.commit()
    conn.close()
conn.execute('''UPDATE flights
SET pilot_id = NULL
WHERE pilot_id IN (1, 5, 6, 8, 9)''')


conn.commit()
conn.close()
