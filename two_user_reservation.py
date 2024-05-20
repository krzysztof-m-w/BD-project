from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DowngradingConsistencyRetryPolicy
from cassandra.query import tuple_factory
from add_reservation import add_reservation
from database_creator import ROOMS, SEATS_IN_ROW, ROWS
import threading
import time


profile = ExecutionProfile(
    retry_policy=DowngradingConsistencyRetryPolicy(),
    consistency_level=ConsistencyLevel.ONE,
    serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
    request_timeout=20,
    row_factory=tuple_factory
)

def reserve_all_seats(user_id, session):
    selection_query = 'select * from seats;'
    result = session.execute(selection_query)
    counter = 0
    for row in result:
        add_reservation(row.room_id, row.row, row.seat_number, user_id, counter, session)
        counter += 1

cluster1 = Cluster(['127.0.0.2'], port=9042, execution_profiles={'default' : profile})
session1 = cluster1.connect('cinema')

cluster2 = Cluster(['127.0.0.3'], port=9042, execution_profiles={'default' : profile})
session2 = cluster2.connect('cinema')

print("start reserving")
t1 = threading.Thread(target=reserve_all_seats, args=(1, session1))
t2 = threading.Thread(target=reserve_all_seats, args=(2, session2))

start_time = time.time()
t1.start()
t2.start()

t1.join()
t2.join()
end_time = time.time()

query = "select user_id from reservations;"
result = session1.execute(query)
count1 = 0
count2 = 0
for row in result:
    if row.user_id == 1:
        count1+=1
    if row.user_id == 2:
        count2+=1

print(f"user1 reserved {count1} seats")
print(f"user2 reserved {count2} seats")
print(f"execution time: {end_time - start_time}")

for room_id in range(1, ROOMS+1):
    query1 = f"delete from reservations where room_id = {room_id};"
    session1.execute(query1)


session1.shutdown()
cluster1.shutdown()
session2.shutdown()
cluster2.shutdown()