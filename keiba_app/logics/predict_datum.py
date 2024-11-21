from keiba_app import app, db, model
from ..models.horse import HorseModel
from ..models.jockey import JockeyModel
from ..models.race_result import RaceResultModel
from ..models.race_calender import RaceCalenderModel
from ..models.predict_result import PredictResultModel
from ..models.return_table import ReturnTableModel
from dateutil.relativedelta import relativedelta

import pandas as pd
from datetime import datetime as dt
from datetime import date

class PredictDatum:
  @staticmethod
  def get_race_datum(race_id: str) -> dict:
    with app.app_context():
      race_data = db.session.query(RaceResultModel).filter(RaceResultModel.race_id == race_id).all()
      return_table = db.session.query(ReturnTableModel).filter(ReturnTableModel.race_id == race_id).first()
    horse_id_list = [race.horse_id for race in race_data]
    jockey_id_list = [race.jockey_id for race in race_data]
    return {'horse_id_list': horse_id_list, 'jockey_id_list': jockey_id_list, 'return_table': return_table.return_data}

  @staticmethod
  def recent_score_of_horses(horse_id_list: list, race_date: date) -> dict:
    with app.app_context():
      horses = [db.session.query(HorseModel).filter(HorseModel.horse_id == horse_id).first() for horse_id in horse_id_list]
    recent_score_of_horses = {}
    for horse in horses:
      if bool(horse):
        recent_date = max((key for key in horse.order_ave_info.keys() if race_date > dt.strptime(key, '%Y-%m-%d').date()), default=None)
        if bool(recent_date):
          recent_score_of_horses[horse.horse_id] = {'馬直近成績': horse.order_ave_info[recent_date]}
        else:
          recent_score_of_horses[horse.horse_id] = {'馬直近成績': None}
    return recent_score_of_horses

  @staticmethod
  def datum_of_jockeies(jockey_id_list: list) -> dict:
    with app.app_context():
      jockeies = [db.session.query(JockeyModel).filter(JockeyModel.jockey_id == jockey_id).first() for jockey_id in jockey_id_list]
    jockey_datum = {}
    for jockey in jockeies:
      jockey_datum[jockey.jockey_id] = {
        '騎手直近単勝率': jockey.top_ratio,
        '騎手直近複勝率': jockey.victory_ratio,
        '騎手経験値': jockey.experience,
        '騎手年齢': jockey.old
        }
    return jockey_datum

  @staticmethod
  def predict(race_id: str) -> dict:
    # 過去全レースでの予測結果をDBに保存
    with app.app_context():
      q = db.session.query(RaceResultModel).filter(RaceResultModel.race_id == race_id)
    race_df = pd.read_sql(q.statement, db.engine)
    race_df_index = [race_id] * len(race_df)
    race_date = race_df['race_date'].tolist()[0]
    horse_numbers = race_df['horse_number'].tolist()
    horse_number_se = pd.Series(horse_numbers, index=race_df_index)
    horse_id_list = race_df['horse_id'].tolist()
    jockey_id_list = race_df['jockey_id'].tolist()

    horse_datum = PredictDatum.recent_score_of_horses(horse_id_list, race_date)
    jockey_datum = PredictDatum.datum_of_jockeies(jockey_id_list)
    horse_df = pd.DataFrame(horse_datum).T
    horse_df.index = [race_id] * len(horse_df)
    jockey_df = pd.DataFrame(jockey_datum).T
    jockey_df.index = [race_id] * len(jockey_df)
    if len(horse_df) == len(race_df) and len(jockey_df) == len(race_df):
      df = pd.concat([jockey_df, horse_df], axis=1)
      prediction = model.predict(df).tolist()
      df['馬番'] = horse_number_se
      df['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
      top_odds = race_df['odds'].tolist()
      top_se = pd.Series(top_odds, index=race_df_index)
      df['単勝オッズ'] = top_se
      return_index = []
      for _, row in df.iterrows():
        try:
          if float(row['単勝オッズ']) <= 130:
            return_index.append(row['競走力指数'] * float(row['単勝オッズ']))
          else:
            return_index.append(row['競走力指数'] * 130)
        except Exception:
          return_index.append(0)
      df['回収指数'] = pd.Series(return_index, index=race_df_index)
    else:
      df = None
    return_table = db.session.query(ReturnTableModel).filter(ReturnTableModel.race_id == race_id).first()
    return_data = return_table.return_data
    return_df = pd.DataFrame(return_data)

    return {'data': df, 'return': return_df}
