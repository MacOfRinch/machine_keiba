# 定期実行ジョブの中身

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

def default_job():
  url = os.getenv('URL_HOST') + '/schedule/update_job'
  print(f'定期実行ジョブが{dt.now()}にリセットされました。')
  requests.post(url)

def test(text):
  print(text)
  print(f'ジョブ無事に実行されてるね。今の時間は{dt.now()}だよ。')

# 毎日AM1:00実行
def get_days_of_race_held():
  from main import app
  with app.app_context():
    from keiba_app.check_if_race_held import add_new_data, delete_old_data
    add_new_data()
    delete_old_data()
  with app.app_context():
    from keiba_app.models.services import get_race_dates
    future_dates = get_race_dates()
  if bool(future_dates):
    days = [str(dt.strptime(date, '%Y%m%d').day) for date in future_dates]
    days_for_cron = ','.join(days)
    print('今日のレースがあることを検知したため、データを取得します')
    return days_for_cron
  else:
    print('今日はレースがありません')
    # 実行させないために一日前の日付を入れる
    return (dt.today() - relativedelta(days=1)).day

# レースがある日に9:00~17:00の間5分ごとに実行
  
