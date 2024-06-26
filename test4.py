from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DowngradingConsistencyRetryPolicy
from cassandra.query import tuple_factory
from add_reservation import add_reservation, remove_reservation
from database_creator import ROOMS, SEATS_IN_ROW, ROWS
import time

profile = ExecutionProfile(
    retry_policy=DowngradingConsistencyRetryPolicy(),
    consistency_level=ConsistencyLevel.ONE,
    serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
    request_timeout=20,
    row_factory=tuple_factory
)

cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9042, execution_profiles={'default' : profile})
session = cluster.connect('cinema')

start_time = time.time()
c = 0
for _ in range(1000):
    r=add_reservation(1, 1, 1, 1, c, session, {})
    remove_reservation(1, 1, 1, 1, session)
    c += 1

end_time = time.time()

print(f"execution time: {end_time - start_time}")

session.shutdown()
cluster.shutdown()