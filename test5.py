from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DowngradingConsistencyRetryPolicy
from cassandra.query import tuple_factory
from add_reservation import add_reservation, alter_reservation
from database_creator import ROOMS, SEATS_IN_ROW, ROWS
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
        r=add_reservation(row.room_id, row.row, row.seat_number, user_id, counter, session, {})
        counter += 1

cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9042, execution_profiles={'default' : profile})
session = cluster.connect('cinema')

reserve_all_seats(1, session)

start_time = time.time()
selection_query = 'select * from seats;'
result = session.execute(selection_query)
counter = 0
for i, row in enumerate(result):
    alter_reservation(row.room_id, row.row, row.seat_number, 1, session, {'discount' : 1})
    

end_time = time.time()

print(f"execution time: {end_time - start_time}")

session.shutdown()
cluster.shutdown()