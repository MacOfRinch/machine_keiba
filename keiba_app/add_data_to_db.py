import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import db
from keiba_app import app
import pandas as pd
from models.race_result import RaceResultModel
from models.race_result import half_year_later

df = pd.read_pickle('../DATA/df_for_db_20240721.pkl')
with app.app_context():
  db.drop_all()
  db.create_all()
  
  for _, row in df.iterrows():
    race_result = RaceResultModel(
      race_id=row['race_id'],
      order=row['order'],
      horse_name=row['horse_name'],
      jockey_name=row['jockey_name'],
      odds=row['odds'],
      race_date=row['race_date'],
      expires_at=half_year_later
    )
    db.session.add(race_result)
  db.session.commit()
