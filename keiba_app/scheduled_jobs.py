# 定期実行ジョブの中身

from datetime import datetime as dt
import time
from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified
import random
import pandas as pd

from keiba_app.models.temporary_race_data import TemporaryRaceData
from keiba_app.models.services import *
from keiba_app.scheduler_json import save_jobs_to_file, scheduler
from keiba_app.logics.new_race import NewRace

# レースがない日に5分毎に実行
def test():
    from keiba_app import db
    from main import app
    with app.app_context():
        races = db.session.query(RaceResultModel).filter(RaceResultModel.race_date >= dt.strftime(dt.today() - relativedelta(months=1), '%Y%m%d')).all()
        random_race = random.choice(races)
        print(random_race.race_id)
        from keiba_app.web_sockets import emit_random_data
        from keiba_app.logics.predict_datum import PredictDatum
        try:
            col = ['order', 'horse_number', 'horse_name', 'jockey_name', 'odds', '競走力指数']
            race_data = PredictDatum.predict(random_race.race_id)['race_data'][col]
            race_data.columns = ['着順', '馬番', '馬名', '騎手', '単勝オッズ', '競走力指数']
            display_data = race_data.to_dict(orient='records')
        except AttributeError:
            test()
    emit_random_data(display_data)

# デバッグ用
def main_test():
    from keiba_app import db
    from main import app
    with app.app_context():
        # 近3レースのid取得
        all_races = db.session.query(RaceCalenderModel).filter(RaceCalenderModel.race_date == '20241201').all()
    all_races.sort(key=lambda x: dt.strptime(x.start_at, '%H:%M'))
    races = [race for race in all_races if dt.strptime(race.start_at, '%H:%M').time() >= dt.now().time()]
    races = races[:3] if len(races) >= 3 else races
    race_ids = [race.race_id for race in races]

    emit_datum = []
    from keiba_app import model
    for race_id in race_ids:
        with app.app_context():
            race_datum = NewRace.scrape(race_id)
            feature = NewRace.analyze('20241201', race_datum['race_df'])
        prediction = model.predict(feature).tolist()
        predict_datum = race_datum['race_df']
        predict_datum['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
        # js側で_以降を削除
        col = ['枠_枠', '馬番_馬番', '馬名_馬名', '騎手_騎手', 'オッズ_オッズ', '競走力指数']
        display_data = predict_datum[col].to_dict(orient='records')
        temporary_return_table = race_datum['odds_df'].to_dict(orient='records')
        emit_datum.append({'race_data': display_data, 'odds_data': temporary_return_table})
        time.sleep(3)
    from keiba_app.web_sockets_hello import emit_main_test_data
    emit_main_test_data(emit_datum)

# 毎日AM1:00実行
def get_days_of_race_held():
    today = dt.strftime(dt.today(), '%Y%m%d')
    from keiba_app import model
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
                race_datum = NewRace.scrape(race_id)
                feature = NewRace.analyze(today, race_datum['race_df'])
                prediction = model.predict(feature).tolist()
                predict_datum = race_datum['race_df']
                predict_datum['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
                col = ['枠_枠', '馬番_馬番', '馬名_馬名', '騎手_騎手', 'オッズ_オッズ', '競走力指数']
                race_info = predict_datum[col]
                start_at = get_start_time(race_id)
                temporary_data = TemporaryRaceData(
                race_id=race_id,
                race_date=future_date,
                race_info=race_info,
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
            for job in scheduler.get_jobs():
                if job.id == 'test':
                    scheduler.remove_job(job.id)
            scheduler.add_job(
                id='get_race_data',
                func=get_race_data,
                trigger='cron',
                day=days_for_cron,
                hour='8-17',
                minute='*/5'
            )
        save_jobs_to_file(scheduler)
    else:
        print('今日はレースがありません')
        from keiba_app import db
        with app.app_context():
            jobs = scheduler.get_jobs()
            job_ids = [job.id for job in jobs]
            if 'get_race_data' in job_ids:
                scheduler.remove_job('get_race_data')
            if 'test' not in job_ids:
                scheduler.add_job(
                    id='test',
                    func=test,
                    trigger='cron',
                    day=dt.strftime(dt.today(), '%d'),
                    hour='*',
                    minute='*/5'
                )
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
        # 近3レースのid取得
        all_races = db.session.query(RaceCalenderModel).filter(RaceCalenderModel.race_date == today).all()
    all_races.sort(key=lambda x: dt.strptime(x.start_at, '%H:%M'))
    races = [race for race in all_races if dt.strptime(race.start_at, '%H:%M').time() >= dt.now().time()]
    races = races[:3] if len(races) > 3 else races
    race_ids = [race.race_id for race in races]

    emit_datum = []
    from keiba_app import model
    for race_id in race_ids:
        with app.app_context():
            race_datum = NewRace.scrape(race_id)
            feature = NewRace.analyze(today, race_datum['race_df'])
            start_at = db.session.query(TemporaryRaceData).filter(TemporaryRaceData.race_id == race_id).first().start_at
        prediction = model.predict(feature).tolist()
        predict_datum = race_datum['race_df']
        predict_datum['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
        # js側で_以降を消す
        col = ['枠_枠', '馬番_馬番', '馬名_馬名', '騎手_騎手', 'オッズ_オッズ', '競走力指数']
        display_data = predict_datum[col].to_dict(orient='records')
        with app.app_context():
            temporary_race_info = db.session.query(TemporaryRaceData).filter(TemporaryRaceData.race_id == race_id).first()
            temporary_race_info.race_info = display_data
            # JSON型のため明示的に変更を通知
            flag_modified(temporary_race_info, 'race_info')
        temporary_return_table = race_datum['odds_df'].to_dict(orient='records')
        emit_datum.append({'race_data': temporary_race_info.race_info, 'odds_data': temporary_return_table, 'start_at': start_at})
        time.sleep(3)
    from keiba_app.web_sockets import emit_new_race_data
    emit_new_race_data(emit_datum)

# 毎週火曜日AM2:00に実行　先週行われたレースの結果を取得する
# def get_race_result():
