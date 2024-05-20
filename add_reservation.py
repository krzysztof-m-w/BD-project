from cassandra.cluster import Cluster

def add_reservation(room_id, row_, seat_number, user_id, user_counter, session):
    select_query1 = f"""SELECT id FROM seats 
    WHERE room_id = {room_id} AND row = '{row_}' AND seat_number = {seat_number};
    """

    result1 = session.execute(select_query1).all()
    seat_id = None


    if result1:
        seat_id = result1[0].id

        select_query2 = f"""SELECT * FROM reservations WHERE room_id = {room_id} AND seat_id = {seat_id};
        """
        result2 = session.execute(select_query2)
        if not result2.all():
            insert_query = f"""INSERT INTO reservations (id, room_id, seat_id, user_id)
            VALUES ({int((1 << 32)*user_id)+user_counter}, {room_id}, {seat_id}, {user_id})"""
            session.execute(insert_query)
            
        else:
            #potential handling of reserved seat
            pass
        

if __name__ == "__main__":
    cluster = Cluster(['127.0.0.2', '127.0.0.3', '127.0.0.4'], port=9042)
    session = cluster.connect('cinema')

    add_reservation(1, 'A', 2, 1, 0, session)

    session.shutdown()
    cluster.shutdown()