from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.2', '127.0.0.3', '127.0.0.4'], port=9042)
session = cluster.connect()

create_keyspace_query = """
CREATE KEYSPACE IF NOT EXISTS cinema
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 2 }
"""

session.execute(create_keyspace_query)


session.shutdown()


cluster.shutdown()