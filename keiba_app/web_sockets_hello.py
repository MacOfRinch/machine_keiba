from keiba_app import socketio
from datetime import datetime as dt
from flask import request
import json

latest_data = {'message': '初期データ', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
# デバッグ用
connected_clients = set()

@socketio.on('connect', namespace='/hello')
def handle_connect():
  client_id = request.sid
  connected_clients.add(client_id)
  print(f'コネクションが確立されました! クライアントID: {client_id}')

  socketio.emit('random_event', latest_data, to=client_id)
  socketio.emit('response', {'message': 'connection成功'}, to=client_id)
  # socketio.start_background_task(target=emit_test_data)

@socketio.on('request_latest_data', namespace='/hello')
def emit_latest_data():
  global latest_data
  if latest_data:
    socketio.emit('connect', latest_data, namespace='/hello')

@socketio.on('receive', namespace='/hello')
def handle_my_custom_event(data):
  print('received json: ' + str(data))

@socketio.on('disconnect', namespace='/hello')
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
    socketio.emit('test_event', latest_data, namespace='/hello')
    print(f'送信成功: {latest_data}')
  else:
    print('エラー: 初期データが存在しません')
  print('イベントが発火しました')

def emit_random_data(race_data):
  global latest_data
  latest_data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
  now_time = latest_data['time'] or dt.strftime(dt.now(), '%H:%M:%S')
  socketio.emit('update_table', {'data': race_data, 'time': now_time}, namespace='/hello')

def emit_new_race_data(datum):
  global latest_data
  latest_data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
  now_time = latest_data['time'] or dt.strftime(dt.now(), '%H:%M:%S')
  # emit_datum.append({'race_data': display_data, 'odds_data': temporary_return_table})
  socketio.emit(
    'update_main_tables',
    {'time': now_time,
      'race_0': datum[0]['race_data'], 'odds_0': datum[0]['odds_data'],
      'race_1': datum[1]['race_data'], 'odds_1': datum[1]['odds_data'],
      'race_2': datum[2]['race_data'], 'odds_2': datum[2]['odds_data']
    }, namespace='/hello'
  )

def emit_main_test_data(datum):
  global latest_data
  latest_data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
  now_time = latest_data['time'] or dt.strftime(dt.now(), '%H:%M:%S')
  print(datum)
  print('--------------------------------------')
  print(datum[0]['race_data'])
  socketio.emit(
    'update_main_tables',
    {'time': now_time, 'message': 'うまくいくかなぁ',
      'race_0': json.dumps(datum[0]['race_data']), 'odds_0': json.dumps(datum[0]['odds_data']),
      'race_1': json.dumps(datum[1]['race_data']), 'odds_1': json.dumps(datum[1]['odds_data']),
      'race_2': json.dumps(datum[2]['race_data']), 'odds_2': json.dumps(datum[2]['odds_data'])
    }, namespace='/hello'
  )
