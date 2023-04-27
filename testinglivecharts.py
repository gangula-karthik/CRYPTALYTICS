# from flask import Flask,render_template,url_for,request,redirect, make_response
# import random
# import json
# from time import time
# from random import random
# from flask import Flask, render_template, make_response
# from wsrealtime import *


# app = Flask(__name__)


# @app.route('/', methods=["GET", "POST"])
# def main():
#     return render_template('index.html')


# @app.route('/data', methods=["GET", "POST"])
# def data():
#     # Data Format
#     # [TIME, Temperature, Humidity]

#     Temperature = random() * 100
#     Humidity = random() * 55
#     url = "wss://stream.binance.com:9443/ws"
#     binance_ws = BinanceWebSocket(url)
    
#     # Start Binance WebSocket and get the data
#     # binance_data = binance_ws.start()

#     data = [time() * 1000, Temperature, Humidity]

#     response = make_response(json.dumps(data))

#     response.content_type = 'application/json'

#     return response


# if __name__ == "__main__":
#     app.run(debug=True)



from threading import Lock
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import requests

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

url = 'https://api.coinbase.com/v2/prices/btc-usd/spot'

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(3)
        count += 1
        price = ((requests.get(url)).json())['data']['amount']
        socketio.emit('my_response',
                      {'data': 'Bitcoin current price (USD): ' + price, 'count': count})

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

# Receive the test request from client and send back a test response
@socketio.on('test_message')
def handle_message(data):
    print('received message: ' + str(data))
    emit('test_response', {'data': 'Test response sent'})

# Broadcast a message to all clients
@socketio.on('broadcast_message')
def handle_broadcast(data):
    print('received: ' + str(data))
    emit('broadcast_response', {'data': 'Broadcast sent'}, broadcast=True)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    socketio.run(app, port=5000)
