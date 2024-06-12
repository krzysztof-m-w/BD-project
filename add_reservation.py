from cassandra.cluster import Cluster
import cassandra

def parse_data_fields(fields : dict):
    field_names = ""
    field_values = ""
    for name in fields.keys():
        field_names += ","
        field_names += name
        field_values += ","
        field_values += str(fields[name])

    return field_names, field_values


def get_reservation(room_id, row_, seat_number, session):
    select_query1 = f"""SELECT id FROM seats 
    WHERE room_id = {room_id} AND row = {row_} AND seat_number = {seat_number};
    """

    result1 = session.execute(select_query1).all()
    seat_id = None

    #seat doesn't exist
    if not result1:
        return (False, False, None, None)
    
    seat_id = result1[0].id

    select_query2 = f"""SELECT * FROM reservations WHERE room_id = {room_id} AND seat_id = {seat_id};
    """
    result2 = session.execute(select_query2).all()

    #seat exists, is not reserved, no reservation data
    if not result2:
        return (True, False, seat_id, None)
    
    return (True, True, seat_id, (result2[0]))


def add_reservation(room_id, row_, seat_number, user_id, user_counter, session, data_fields):
    
    seat_exists, is_reserved, seat_id,  data = get_reservation(room_id, row_, seat_number, session)

    if seat_exists and not is_reserved:
        field_names, field_values = parse_data_fields(data_fields)

        insert_query = f"""INSERT INTO reservations (id, room_id, seat_id, user_id {field_names})
        VALUES ({int((1 << 32)*user_id)+user_counter}, {room_id}, {seat_id}, {user_id} {field_values})"""
        session.execute(insert_query)

def remove_reservation(room_id, row_, seat_number, user_id, session):

    seat_exists, is_reserved, seat_id,  data = get_reservation(room_id, row_, seat_number, session)

    if seat_exists and is_reserved and user_id == data.user_id:
        delete_query = f"""DELETE  FROM Reservations WHERE room_id = {room_id} AND seat_id = {seat_id}"""
        session.execute(delete_query)


def alter_reservation(room_id, row_, seat_number, user_id, session, altered_fields={}):
    seat_exists, is_reserved, seat_id,  data = get_reservation(room_id, row_, seat_number, session)

    if seat_exists and is_reserved and user_id == data.user_id:
        field_names, field_values = parse_data_fields(altered_fields)

        insert_query = f"""INSERT INTO reservations (id, room_id, seat_id, user_id {field_names})
        VALUES ({data.id}, {room_id}, {seat_id}, {user_id} {field_values})"""
        try:
            session.execute(insert_query)
        except cassandra.InvalidRequest:
            print("invalid request")
        

if __name__ == "__main__":
    cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9042)
    session = cluster.connect('cinema')

    add_reservation(1, 1, 2, 1, 0, session, {})
    alter_reservation(1, 1, 2, 1, session, {'discount' : 0})

    session.shutdown()
    cluster.shutdown()