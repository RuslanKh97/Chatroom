from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt
from flask_socketio import emit, SocketIO


app = Flask(__name__)
socket = SocketIO(app)

app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_URI'] = 'mongodb://pretty:printed@ds021731.mlab.com:21731/mongologinexample'

mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        return render_template('client.html')

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')


@socket.on('connect')
def connect():
    print("[CLIENT CONNECTED]:", request.sid)

    @socket.on('disconnect')
    def disconn():
        print("[CLIENT DISCONNECTED]:", request.sid)

    @socket.on('notify')
    def notify(user):
        emit('notify', user, broadcast=True, skip_sid=request.sid)

    @socket.on('data')
    def emitback(data):
        emit('returndata', data, broadcast=True)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
    socket.run(app)