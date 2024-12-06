# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import socketio
from datetime import datetime as dt
from flask import request

latest_data = {'message': '初期データ', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
# デバッグ用
connected_clients = set()

@socketio.on('connect', namespace='/')
def handle_connect(latest_data):
  client_id = request.sid
  connected_clients.add(client_id)
  print(f'コネクションが確立されました! クライアントID: {client_id}')
  if latest_data:
    socketio.emit('random_event', latest_data, namespace='/')
  socketio.emit('response', {'message': 'connection成功'}, to=client_id)
  # socketio.start_background_task(target=emit_test_data)

@socketio.on('request_latest_data', namespace='/')
def emit_latest_data():
  global latest_data
  if latest_data:
    socketio.emit('connect', latest_data, namespace='/')

@socketio.on('receive', namespace='/')
def handle_my_custom_event(data):
  print('received json: ' + str(data))

@socketio.on('disconnect', namespace='/')
def handle_disconnect():
  client_id = request.sid
  connected_clients.discard(client_id)
  print(f'コネクションが解除されました クライアントID: {request.sid}')

# デバッグ用
def emit_test_data():
  print("クライアントが最新データを要求しました")
  global latest_data
  latest_data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
  if latest_data:
    socketio.emit('test_event', latest_data, namespace='/')
    print(f'送信成功: {latest_data}')
  else:
    print('エラー: 初期データが存在しません')
  print('イベントが発火しました')

def emit_random_data(race_data):
  global latest_data
  latest_data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
  now_time = latest_data['time'] or dt.strftime(dt.now(), '%H:%M:%S')
  socketio.emit('update_table', {'data': race_data, 'time': now_time})
