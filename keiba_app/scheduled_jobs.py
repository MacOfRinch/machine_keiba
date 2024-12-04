# 定期実行ジョブの中身

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime as dt
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
from sqlalchemy import text

from keiba_app.models.temporary_race_data import TemporaryRaceData
from keiba_app.models.services import *
from keiba_app.scheduler_json import save_jobs_to_file, scheduler

def default_job():
    url = os.getenv('URL_HOST') + '/schedule/update_job'
    print(f'定期実行ジョブが{dt.now()}にリセットされました。')
    requests.post(url)

def test():
    print(f'ジョブ無事に実行されてるね。今の時間は{dt.now()}だよ。')
    data = {'message': 'こんちわ！', 'time': dt.strftime(dt.now(), '%H:%M:%S')}
    from keiba_app.web_sockets import emit_data_to_client
    emit_data_to_client(data)

# 毎日AM1:00実行
def get_days_of_race_held():
    from main import app
    with app.app_context():
        from keiba_app.check_if_race_held import add_new_data, delete_old_data
        add_new_data()
        delete_old_data()
    with app.app_context():
        future_dates = get_race_dates()
        if bool(future_dates):
            from keiba_app import db
            for future_date in future_dates:
                future_race_ids = get_race_ids(future_date)
            for race_id in future_race_ids:
                start_at = get_start_time(race_id)
                temporary_data = TemporaryRaceData(
                race_id=race_id,
                race_date=future_date,
                start_at=start_at
                )
                db.session.add(temporary_data)
            db.session.commit()
    if bool(future_dates):
        days = [str(dt.strptime(date, '%Y%m%d').day) for date in future_dates]
        days = list(set(days))
        days_for_cron = ','.join(days)
        print('今日のレースがあることを検知したため、データを取得します')
        with app.app_context():
            scheduler.add_job(
                id='get_race_data',
                func=get_race_data,
                trigger='cron',
                day=days_for_cron,
                hour='9-17',
                minute='*/10'
            )
        save_jobs_to_file(scheduler)
    else:
        print('今日はレースがありません')
        from keiba_app import db
        with app.app_context():
            for job in scheduler.get_jobs():
                if job.id == 'get_race_data':
                    scheduler.remove_job(job.id)
        save_jobs_to_file(scheduler)
        with app.app_context():
            db.session.query(TemporaryRaceData).delete()
            db.session.execute(text('OPTIMIZE TABLE temporary_race_data;'))
            print('temporary_dataを削除しました')
            db.session.commit()
    if not scheduler.running:
        scheduler.start()

# レースがある日に8:00~17:00の間5分ごとに実行
def get_race_data():
    print('レースデータの取得を開始します')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    today = dt.today().strftime('%Y%m%d')
    from keiba_app import db
    from main import app
    with app.app_context():
        race_ids = [race_id_tupple[0] for race_id_tupple in db.session.query(TemporaryRaceData.race_id).filter(TemporaryRaceData.race_date == today).all()]
    for race_id in race_ids:
        url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + race_id
        # try:
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        sub_text = soup.find('div', attrs={'class': 'RaceData01'}).text
        start_at_str = ''.join(re.findall(r'\d{1,2}:\d{1,2}', sub_text)[0])
        start_at = dt.strptime(start_at_str, '%H:%M').time()
        with app.app_context():
            temporary_race_data = db.session.query(TemporaryRaceData).filter(TemporaryRaceData.race_id == race_id).first()
        scheduled_start_at = dt.strptime(temporary_race_data.start_at, '%H:%M').time()
        last_updated = dt.now().time()
        print(start_at)
        print(last_updated)
        time.sleep(3)
    from keiba_app import socketio
    socketio.emit()
        # except Exception as e:
        #     print(e)
        #     time.sleep(3)
        #     continue
