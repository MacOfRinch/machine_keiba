import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import db
from keiba_app import app
import pandas as pd
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from models.race_result import RaceResultModel
from models.horse import HorseModel
from models.jockey import JockeyModel

df = pd.read_pickle('../DATA/df_for_db_20240721.pkl')
horse_df = pd.read_pickle('../DATA/horse_df_for_db_20240801.pkl')
jockey_df = pd.read_pickle('../DATA/jockey_df_for_db_20240801.pkl')
with app.app_context():
  db.drop_all()
  db.create_all()
  
  for _, row in df.iterrows():
    race_result = RaceResultModel(
      race_id=row['race_id'],
      order=row['order'],
      horse_id=row['horse_id'],
      horse_name=row['horse_name'],
      jockey_id=row['jockey_id'],
      jockey_name=row['jockey_name'],
      odds=row['odds'],
      race_date=row['race_date'],
      expires_at=row['race_date']+relativedelta(months=6),
      predict_flag=True
    )
    db.session.add(race_result)

  for _, row in horse_df.iterrows():
    horse_data = HorseModel(
      horse_id=row['horse_id'],
      order_ave=row['order_ave'],
      expires_at=dt.today()+relativedelta(months=6)
    )
    db.session.add(horse_data)

  for _, row in jockey_df.iterrows():
    jockey_data = JockeyModel(
      jockey_id=row['騎手id'],
      old=row['騎手年齢'],
      top_ratio=row['騎手直近単勝率'],
      victory_ratio=row['騎手直近複勝率'],
      experience=row['騎手経験値'],
      expires_at=dt.today()+relativedelta(months=6)
    )
    db.session.add(jockey_data)
  db.session.commit()
