from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET'] = "secret123"
socketio = SocketIO(app, cors_allowed_origins='*')



@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    socketio.run(app, host='localhost',allow_unsafe_werkzeug=True)