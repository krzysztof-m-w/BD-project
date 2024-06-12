from flask import Flask, render_template
from add_reservation import *
from cassandra.cluster import Cluster
import cassandra
app = Flask(__name__)

@app.route('/')  
def home():   
    rooms = [f"Room {i+1}" for i in range(10)]
    return render_template('index.html', rooms=rooms)

@app.route('/room/<int:room_id>')
def room(room_id): 
    return render_template('room.html', room_id=room_id)

if __name__ == '__main__':
    cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9042)
    session = cluster.connect('cinema')
    app.run(debug=True)
