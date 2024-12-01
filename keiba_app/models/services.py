# DB内のデータを外部に出力するためのファイル

from keiba_app.models.race_calender import RaceCalenderModel
from keiba_app import db
from datetime import datetime as dt
from keiba_app.models.race_result import RaceResultModel
from keiba_app.models.horse import HorseModel
from keiba_app.models.jockey import JockeyModel
from keiba_app.models.race_calender import RaceCalenderModel
from keiba_app.models.predict_result import PredictResultModel

def get_race_dates():
  from main import app
  with app.app_context():
    scheduled_races = db.session.query(RaceCalenderModel).all()
  future_dates = [race.race_date for race in scheduled_races if dt.strptime(race.race_date, '%Y%m%d').date() >= dt.today().date()]
  return future_dates

def get_race_ids(date):
  from main import app
  with app.app_context():
    race_ids = [race_id_tupple[0] for race_id_tupple in db.session.query(RaceCalenderModel.race_id).filter(RaceCalenderModel.race_date == date).all()]
  return race_ids

def get_start_time(race_id):
  from main import app
  with app.app_context():
    start_at = db.session.query(RaceCalenderModel.start_at).filter(RaceCalenderModel.race_id == race_id).first()
  return start_at[0]
