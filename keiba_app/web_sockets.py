# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from keiba_app import socketio
from keiba_app.models.services import RaceCalenderModel
from datetime import datetime as dt
import time

# def register_websocket_events():
@socketio.on('connect')
def handle_connect():
  print('コネクションが確立されました！')
  socketio.start_background_task(target=emit_data_to_client)

@socketio.on('disconnect')
def handle_disconnect():
  print('コネクションが解除されました')

def emit_data_to_client(data):
  # socketio.emit('update', {'message': '今更新されたよ！'})
  socketio.emit('test_job', data)
