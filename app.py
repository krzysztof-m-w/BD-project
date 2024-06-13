from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from add_reservation import *
from cassandra.cluster import Cluster
import cassandra
import docker
from docker.errors import APIError
from flask_session import Session
import uuid
import time
import hashlib


app = Flask(__name__)







app.config['SESSION_TYPE'] = 'filesystem' 
app.secret_key = 'supersecretkey' 
Session(app)

def get_user_id():
    if 'user_id' not in session:
        i=uuid.uuid4().bytes
        session['user_id'] = int(hashlib.sha256(i).hexdigest()[:7], 16) # Assign a random unique user ID
        
        session['user_counter'] = 0  # Initialize the counter
    return session['user_id']



def avail():
    avail=[]
    for x in range(1,11):
        r,_=get_seats(x)
        avail.append(100-len(r))
    return avail
@app.route('/') 

def home(): 
    get_user_id()
    
    rooms = [f"Room {i+1}" for i in range(10)]
    return render_template('index.html', rooms=rooms, available=available, zip=zip)

def get_seats(room_id):
    reserved=[]
    user=[]
    for x in range(1,11):
        for y in range(1,11):
            seat_exists, is_reserved, seat_id,  data = get_reservation(room_id, x, y, cass_session)
            
            if is_reserved:
                print(data)
                seat_num=seat_id%100+1
                reserved.append(int(seat_num))
                user.append(data.user_id)
    return reserved, user


@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def room(room_id):
    reserved_seats, users=get_seats(room_id)
    if request.method == 'POST':
        selected_seat = request.form.get('selected_seat')
        discount=request.form.get('discountRadio')
        
        if selected_seat:
            row=(int(selected_seat)-1)//10+1
            seat=int(selected_seat[-1]) 
            if seat==0:
                seat=10
               
            res=add_reservation(int(room_id), int(row),int(seat), int(session['user_id']), int(session['user_counter']), cass_session, {'discount': int(discount) if discount else 0})
            reserved_seats, users=get_seats(room_id)

            if res is not None and users[reserved_seats.index(int(selected_seat))]==int(session['user_id']):
                flash('Reservation completed', 'success')
                session['user_counter']+=1
                available[room_id-1]-=1
            else:
                flash('Reservation failed', 'warning')
            return render_template('room.html', room_id=room_id, reserved_seats=reserved_seats, users=users)
    return render_template('room.html', room_id=room_id, reserved_seats=reserved_seats, users=users)

@app.route('/edit/<int:room_id>', methods=['GET', 'POST'])
def edit(room_id):
    reserved_seats, users=get_seats(room_id)
    discount=request.form.get('discountRadio')
    uid=int(session['user_id'])
    r_filtered=[reserved_seats[x] for x in range(len(reserved_seats)) if users[x]==uid]
    if request.method == 'POST':
        selected_seat = request.form.get('selected_seat')
        if selected_seat:
            row=(int(selected_seat)-1)//10+1
            seat=int(selected_seat[-1]) 
            if seat==0:
                seat=10

            remove_reservation(int(room_id), int(row), int(seat), int(session['user_id']),  cass_session)
            reserved_seats, users=get_seats(room_id)
            r_filtered=[reserved_seats[x] for x in range(len(reserved_seats)) if users[x]==uid]
            available[room_id-1]+=1
            flash('Succesfully deleted', 'success')
            return render_template('edit.html', room_id=room_id, reserved_seats=r_filtered, users=users)
    return render_template('edit.html', room_id=room_id, reserved_seats=r_filtered, users=users)

@app.route('/update/<int:room_id>', methods=['GET', 'POST'])
def update(room_id):
    reserved_seats, users=get_seats(room_id)
    discount=request.form.get('discountRadio')
    uid=int(session['user_id'])
    r_filtered=[reserved_seats[x] for x in range(len(reserved_seats)) if users[x]==uid]
    if request.method == 'POST':
        selected_seat = request.form.get('selected_seat')
        if selected_seat:
            row=(int(selected_seat)-1)//10+1
            seat=int(selected_seat[-1]) 
            if seat==0:
                seat=10

            alter_reservation(int(room_id), int(row), int(seat), int(session['user_id']),  cass_session, {'discount': int(discount)})
            reserved_seats, users=get_seats(room_id)
            r_filtered=[reserved_seats[x] for x in range(len(reserved_seats)) if users[x]==uid]
      
            flash('Succesfully updated', 'success')
            return render_template('edit.html', room_id=room_id, reserved_seats=r_filtered)
    return render_template('edit.html', room_id=room_id, reserved_seats=r_filtered)



def connect_to_cassandra():
    while True:
        try:
            cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9042)
            session = cluster.connect('cinema')
            print("Connected to Cassandra")
            return session
        except Exception as e:
            print(f"Failed to connect to Cassandra: {e}")
            print("Retrying in 3 seconds...")
            time.sleep(3)


if __name__ == '__main__':
    client=docker.from_env()
    containers=client.containers.list(all=True)
    for container in containers:
        if container.status != 'running' and container.name in ['cas1', 'cas2', 'cas3']:
            try:
                print(f"Starting container {container.name} with ID {container.id}")
                container.start()
                print(f"Container {container.name} started successfully.")
            except APIError as e:
                print(f"Failed to start container {container.name}: {e}")


    cass_session =  connect_to_cassandra()
    available=avail()
    app.run(debug=True)
