from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.2', '127.0.0.3', '127.0.0.4'], port=9042)
session = cluster.connect('cinema')

create_seats_table_query = """CREATE TABLE IF NOT EXISTS seats( 
        id int, 
        room_id int, 
        row text, 
        number int,  
        PRIMARY KEY(id, room_id)
    ) WITH CLUSTERING ORDER BY (room_id ASC);"""

session.execute(create_seats_table_query)

create_reservations_table_query = """CREATE TABLE IF NOT EXISTS reservations(
    id int,
    seat_id int,
    room_id int,
    user_id int,
    PRIMARY KEY(id, seat_id, room_id)
);
"""

session.execute(create_reservations_table_query)

session.shutdown()
cluster.shutdown()