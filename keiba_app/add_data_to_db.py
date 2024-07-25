import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import db
from keiba_app import app
import pandas as pd
from datetime import datetime as dt
from models.race_result import RaceResultModel

df = pd.read_pickle('../DATA/df_for_db_20240721.pkl')
with app.app_context():
  db.drop_all()
  db.create_all()
  
  for _, row in df.iterrows():
    race_result = RaceResultModel(
      race_id=row['race_id'],
      order=row['order'],
      horse_id='0',
      horse_name=row['horse_name'],
      jockey_id='0',
      jockey_name=row['jockey_name'],
      odds=row['odds'],
      race_date=row['race_date'],
      expires_at=dt.today(),
      predict_flag=True
    )
    db.session.add(race_result)
  db.session.commit()
