# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import db
# from ..logics.get_datum import half_year_later
# half_year_later = dt.now() + relativedelta(months=6)

#テストデータ入力用
db.metadata.clear()

class RaceResultModel(db.Model):
  __tablename__ = 'race_result'
  id = db.Column(db.Integer, primary_key=True)
  race_id = db.Column(db.String(255))
  order = db.Column(db.String(255))
  horse_name = db.Column(db.String(255))
  horse_id = db.Column(db.String(255))
  jockey_name = db.Column(db.String(255))
  jockey_id = db.Column(db.String(255))
  odds = db.Column(db.String(255))
  race_date = db.Column(db.Date, nullable=False)
  expires_at = db.Column(db.Date, nullable=False)
  predict_frag = db.Column(db.Boolean, nullable=False, default=True)

  def __init__(self, race_id, order, horse_name, horse_id, jockey_name, jockey_id, odds, race_date, expires_at, predict_flag):
    self.race_id = race_id
    self.order = order
    self.horse_name = horse_name
    self.horse_id = horse_id
    self.jockey_name = jockey_name
    self.jockey_id = jockey_id
    self.odds = odds
    self.race_date = race_date
    self.expires_at = expires_at
    self.predict_frag = predict_flag
