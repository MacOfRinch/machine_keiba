from keiba_app import app, db, model
from ..models.horse import HorseModel
from ..models.jockey import JockeyModel
from ..models.race_result import RaceResultModel
from ..models.race_calender import RaceCalenderModel
from ..models.predict_result import PredictResultModel
from ..models.return_table import ReturnTableModel
from keiba_app import PredictDatum

from dateutil.relativedelta import relativedelta
from sqlalchemy import asc
import pandas as pd
from datetime import datetime as dt
from datetime import date

class OddsUpperLimit:
  @staticmethod
  def calc_fukushou():
    with app.app_context():
      past_1_month_datum = db.session.query(RaceResultModel.race_id).\
        filter(RaceResultModel.race_date >= dt.today() - relativedelta(months=1)).group_by(RaceResultModel.race_id).all()
    race_ids = [race_id[0] for race_id in past_1_month_datum]

    limit = 130
    result = 0
    all_result = 0
    # while limit <= 300:
    for race_id in race_ids:
      # try:
      with app.app_context():
        q = db.session.query(RaceResultModel).filter(RaceResultModel.race_id == race_id)
      race_df = pd.read_sql(q.statement, db.engine)
      df = PredictDatum.predict(race_id)['data']
      if isinstance(df, pd.DataFrame):
        limited_odds = []
        for odds in race_df['odds'].tolist():
          try:
            if float(odds) > limit:
              limited_odds.append(limit)
            else:
              limited_odds.append(float(odds))
          except Exception as e:
            limited_odds.append(0)
            continue
        race_df['odds'] = limited_odds
        race_index = [race_id] * len(limited_odds)
        race_se = pd.Series(limited_odds, index=race_index)
        horse_numbers = race_df['horse_number'].tolist()
        horse_number_se = pd.Series(horse_numbers, index=race_index)
        new_df = pd.concat([df, race_se, horse_number_se], axis=1)
        return_ratio = []
        for _, row in new_df.iterrows():
          return_ratio.append(row['競走力指数'] * row[0])
        new_df['回収指数'] = return_ratio
        delicious_horse_number = new_df[new_df['回収指数'] == new_df['回収指数'].max()][1].values[0]
        return_table = db.session.query(ReturnTableModel).filter(ReturnTableModel.race_id == race_id).first()
        return_data = return_table.return_data
        if delicious_horse_number in return_data['複勝'].keys():
          result += int(return_data['複勝'][delicious_horse_number].replace(',', ''))
          all_result += 100
        else:
          all_result += 100
      else:
        continue
      # except Exception as e:
      #   print(e)
      #   continue
    print(f'limit{limit}のとき回収額{result}')
    print(f'賭けた総額: {all_result}')
    # limit += 10
      # limit130で最大
  
  @staticmethod
  def calc_wide():
    with app.app_context():
      past_1_month_datum = db.session.query(RaceResultModel.race_id).\
        filter(RaceResultModel.race_date >= dt.today() - relativedelta(months=1)).group_by(RaceResultModel.race_id).all()
    race_ids = [race_id[0] for race_id in past_1_month_datum]

    limit = 130
    result = 0
    all_result = 0
    # while limit <= 300:
    for race_id in race_ids:
      # try:
      with app.app_context():
        q = db.session.query(RaceResultModel).filter(RaceResultModel.race_id == race_id)
      race_df = pd.read_sql(q.statement, db.engine)
      df = PredictDatum.predict(race_id)['data']
      if isinstance(df, pd.DataFrame):
        limited_odds = []
        for odds in race_df['odds'].tolist():
          try:
            if float(odds) > limit:
              limited_odds.append(limit)
            else:
              limited_odds.append(float(odds))
          except Exception:
            limited_odds.append(0)
            continue
        race_df['odds'] = limited_odds
        race_index = [race_id] * len(limited_odds)
        odds_se = pd.Series(limited_odds, index=race_index)
        horse_numbers = race_df['horse_number'].tolist()
        horse_number_se = pd.Series(horse_numbers, index=race_index)
        new_df = pd.concat([df, odds_se, horse_number_se], axis=1)
        return_ratio = []
        for _, row in new_df.iterrows():
          return_ratio.append(row['競走力指数'] * row[0])
        new_df['回収指数'] = return_ratio
        delicious_horse_number = new_df[new_df['回収指数'] == new_df['回収指数'].max()][1].values[0]
        return_table = db.session.query(ReturnTableModel).filter(ReturnTableModel.race_id == race_id).first()
        return_data = return_table.return_data
        if delicious_horse_number in return_data['複勝'].keys():
          result += int(return_data['複勝'][delicious_horse_number].replace(',', ''))
          all_result += 100
        else:
          all_result += 100
      else:
        continue
      # except Exception as e:
      #   print(e)
      #   continue
    print(f'limit{limit}のとき回収額{result}')
    print(f'賭けた総額: {all_result}')
    # limit += 10
      # limit130で最大
