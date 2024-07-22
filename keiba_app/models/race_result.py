# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import db
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

half_year_later = dt.now() + relativedelta(months=6)

class RaceResultModel(db.Model):
  __tablename__ = 'race_result'
  id = db.Column(db.Integer, primary_key=True)
  race_id = db.Column(db.String(255))
  order = db.Column(db.String(255))
  horse_name = db.Column(db.String(255))
  jockey_name = db.Column(db.String(255))
  odds = db.Column(db.String(255))
  race_date = db.Column(db.DateTime, nullable=False)
  expires_at = db.Column(db.DateTime, nullable=False, default=half_year_later)

  def __init__(self, race_id, order, horse_name, jockey_name, odds, race_date, expires_at):
    self.race_id = race_id
    self.order = order
    self.horse_name = horse_name
    self.jockey_name = jockey_name
    self.odds = odds
    self.race_date = race_date
    self.expires_at = expires_at
