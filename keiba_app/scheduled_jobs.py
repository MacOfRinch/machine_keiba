# 定期実行ジョブの中身

# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime as dt
import time
from sqlalchemy import text
import random
import pandas as pd

from keiba_app.models.temporary_race_data import TemporaryRaceData
from keiba_app.models.services import *
from keiba_app.scheduler_json import save_jobs_to_file, scheduler
from keiba_app.logics.new_race import NewRace

def test():
    from keiba_app import db
    from main import app
    with app.app_context():
        races = db.session.query(RaceResultModel).filter(RaceResultModel.race_date == '20241201').all()
        random_race = random.choice(races)
        from keiba_app.web_sockets import emit_random_data
        from keiba_app.logics.predict_datum import PredictDatum
        race_data = PredictDatum.predict(random_race.race_id)['data'].to_dict(orient='records')
    emit_random_data(race_data)
    # return random_race

def main_test():
    from keiba_app import db
    from main import app
    with app.app_context():
        # 近3レースのid取得 コレホントにできる？要確認
        race_ids = [race_id_tupple[0] for race_id_tupple in\
            db.session.query(RaceCalenderModel.race_id).filter(RaceCalenderModel.race_date == '20241201').\
            limit(3).all()]
    print(race_ids)

    emit_datum = []
    from keiba_app import model
    for race_id in race_ids:
        with app.app_context():
            race_datum = NewRace.scrape(race_id)
            feature = NewRace.analyze('20241201', race_datum['race_df'])
        prediction = model.predict(feature).tolist()
        predict_datum = race_datum['race_df']
        predict_datum['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
        # col = [('枠', '枠'), ('馬番', '馬番'), ('馬名', '馬名'), ('騎手', '騎手'), ('オッズ', 'オッズ'), ('競走力指数', '')]
        col = ['枠_枠', '馬番_馬番', '馬名_馬名', '騎手_騎手', 'オッズ_オッズ', '競走力指数']
        display_data = predict_datum[col].to_dict(orient='records')
        temporary_return_table = race_datum['odds_df'].to_dict(orient='records')
        emit_datum.append({'race_data': display_data, 'odds_data': temporary_return_table})
        time.sleep(3)
    from keiba_app.web_sockets_hello import emit_main_test_data
    emit_main_test_data(emit_datum)

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
    today = dt.today().strftime('%Y%m%d')
    from keiba_app import db, model
    from main import app
    with app.app_context():
        # 近3レースのid取得 コレホントにできる？要確認
        race_ids = [race_id_tupple[0] for race_id_tupple in\
            db.session.query(TemporaryRaceData.race_id).filter(TemporaryRaceData.race_date == today).\
            filter(dt.strptime(TemporaryRaceData.start_at, '%H:%M').time() >= dt.now().time()).\
            order_by(dt.strptime(TemporaryRaceData.start_at, '%H:%M').time()).limit(3).all()]
    print(race_ids)

    emit_datum = []
    for race_id in race_ids:
        race_datum = NewRace.scrape(race_id)
        feature = NewRace.analyze(today, race_datum['race_df'])
        prediction = model.predict(feature).tolist()
        predict_datum = race_datum['race_df']
        predict_datum['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
        col = [('枠', '枠'), ('馬番', '馬番'), ('馬名', '馬名'), ('騎手', '騎手'), ('オッズ', 'オッズ'), ('競走力指数', '')]
        display_data = predict_datum[col].to_dict(orient='records')
        temporary_return_table = race_datum['odds_df'].to_dict(orient='records')
        emit_datum.append({'race_data': display_data, 'odds_data': temporary_return_table})
        time.sleep(3)
    from keiba_app.web_sockets import emit_new_race_data
    emit_new_race_data(emit_datum)
        # except Exception as e:
        #     print(e)
        #     time.sleep(3)
        #     continue
