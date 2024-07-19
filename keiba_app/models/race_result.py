from keiba_app.main import db
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

half_year_later = dt.now + relativedelta(months=6)

class RaceResultModel(db.Model):
  __tablename__ = 'race_result'
  id = db.Column(db.Integer, primary_key=True)
  race_id = db.Column(db.Integer)
  horse_name = db.Column(db.String(255))
  jockey_name = db.Column(db.String(255))
  is_top = db.Column(db.Boolean)
  is_second = db.Column(db.Boolean)
  is_victory = db.Column(db.Boolean)
  race_date = db.Column(db.Date, nullable=False)
  expired_at = db.Column(db.DateTime, nullable=False, default=half_year_later)

  def __init__(self, race_id, horse_name, jockey_name, is_top, is_second, is_victory, race_date):
    self.race_id = race_id
    self.horse_name = horse_name
    self.jockey_name = jockey_name
    self.is_top = is_top
    self.is_second = is_second
    self.is_victory = is_victory
    self.race_date = race_date
