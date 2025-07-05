from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
socketio = SocketIO(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))

class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    room = db.Column(db.String(50))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = generate_password_hash(request.form['password'])
        db.session.add(User(username=uname, password=pwd))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user'] = uname
            return redirect(url_for('index'))
        else:
            return 'Invalid login'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        room = request.form['room']
        return redirect(url_for('room', room=room))
    return redirect(url_for('index'))

@app.route('/room/<room>')
def room(room):
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('room.html', room=room)



@app.route('/upload/<room>', methods=['POST'])
def upload(room):
    file = request.files['file']
    filename = file.filename
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    db.session.add(SharedFile(filename=filename, room=room))
    db.session.commit()
    socketio.emit('file_shared', {'filename': filename}, room=room)
    return 'OK'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"{session['user']} joined the room."}, room=room)

@socketio.on('signal')
def handle_signal(data):
    emit('signal', data, room=data['room'], include_self=False)

@socketio.on('drawing')
def handle_drawing(data):
    emit('drawing', data, room=data['room'], include_self=False)



if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
