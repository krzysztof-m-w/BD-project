from cassandra.cluster import Cluster
from add_reservation import add_reservation
from database_creator import ROOMS, SEATS_IN_ROW, ROWS
import threading
import string

def reserve_all_seats(user_id, session):
    counter = 0
    for room_id in range(1, ROOMS+1):
        for row in string.ascii_uppercase[:ROWS]:
            for seat_number in range(1, SEATS_IN_ROW+1):
                add_reservation(room_id, row, seat_number, user_id, counter, session)
                counter += 1

cluster = Cluster(['127.0.0.2', '127.0.0.3', '127.0.0.4'], port=9042)
session = cluster.connect('cinema')

print("start reserving")
t1 = threading.Thread(target=reserve_all_seats, args=(1, session))
t2 = threading.Thread(target=reserve_all_seats, args=(2, session))
t1.start()
t2.start()

t1.join()
t2.join()

query = "select user_id from reservations;"
result = session.execute(query)
count1 = 0
count2 = 0
for row in result:
    if row.user_id == 1:
        count1+=1
    if row.user_id == 2:
        count2+=1

print(f"user1 reserved {count1} seats")
print(f"user2 reserved {count2} seats")

for room_id in range(1, ROOMS+1):
    query1 = f"delete from reservations where room_id = {room_id};"
    session.execute(query1)


session.shutdown()
cluster.shutdown()