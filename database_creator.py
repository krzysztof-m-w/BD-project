from cassandra.cluster import Cluster
import string

ROOMS = 10
ROWS = 10
SEATS_IN_ROW = 10


cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9042)
session = cluster.connect('cinema')

create_seats_table_query = """CREATE TABLE IF NOT EXISTS seats( 
        id int, 
        room_id int, 
        row int, 
        seat_number int,  
        PRIMARY KEY(room_id, row, seat_number)
    );"""

session.execute(create_seats_table_query)

create_reservations_table_query = """CREATE TABLE IF NOT EXISTS reservations(
    id bigint,
    seat_id int,
    room_id int,
    user_id int,
    discount int,
    PRIMARY KEY(room_id, seat_id)
);
"""

session.execute(create_reservations_table_query)

id = 0
for room_id in range(1, ROOMS+1):
    for row in range(1, ROWS+1):
        for seat_number in range(1, SEATS_IN_ROW+1):

            add_query = f"""INSERT INTO seats
            (id, room_id, row, seat_number) VALUES
            ({id}, {room_id}, {row}, {seat_number});"""
            
            session.execute(add_query)
            id += 1

session.shutdown()
cluster.shutdown()