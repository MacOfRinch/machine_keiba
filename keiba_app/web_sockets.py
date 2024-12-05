# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import socketio
from datetime import datetime as dt

@socketio.on('connect')
def handle_connect():
  print('コネクションが確立されました！')
  socketio.start_background_task(target=emit_test_data)

@socketio.on('receive')
def handle_my_custom_event(data):
  print('received json: ' + str(data))

@socketio.on('disconnect')
def handle_disconnect():
  print('コネクションが解除されました')

def emit_test_data():
  print(f'ジョブ無事に実行されてるね。今の時間は{dt.now()}だよ。')
  data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
  print(data)
  socketio.emit('test_event', data)
  print('イベントが発火しました')
