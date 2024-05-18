from cassandra.cluster import Cluster
import string

ROOMS = 2
ROWS = 4
SEATS_IN_ROW = 4


cluster = Cluster(['127.0.0.2', '127.0.0.3', '127.0.0.4'], port=9042)
session = cluster.connect('cinema')

create_seats_table_query = """CREATE TABLE IF NOT EXISTS seats( 
        id int, 
        room_id int, 
        row text, 
        seat_number int,  
        PRIMARY KEY(room_id, row, seat_number)
    );"""

session.execute(create_seats_table_query)

create_reservations_table_query = """CREATE TABLE IF NOT EXISTS reservations(
    id bigint,
    seat_id int,
    room_id int,
    user_id int,
    PRIMARY KEY(room_id, seat_id, id)
);
"""

session.execute(create_reservations_table_query)

id = 0
for room_id in range(1, ROOMS+1):
    for row in string.ascii_uppercase[:ROWS]:
        for seat_number in range(1, SEATS_IN_ROW):

            add_query = f"""INSERT INTO seats
            (id, room_id, row, seat_number) VALUES
            ({id}, {room_id}, '{row}', {seat_number});"""
            
            session.execute(add_query)
            id += 1

session.shutdown()
cluster.shutdown()