from keiba_app import db
# from ..logics.get_datum import half_year_later

class RaceCalenderModel(db.Model):
  __tablename__ = 'race_dates'
  __table_args__ = {'extend_existing': True}
  id = db.Column(db.Integer, primary_key=True)
  race_date = db.Column(db.String(255))
  race_title = db.Column(db.String(255))
  race_id = db.Column(db.String(255))
  start_at = db.Column(db.String(255))
  expires_at = db.Column(db.Date, nullable=False)

  def __init__(self, race_date, race_title, race_id, start_at, expires_at):
    self.race_date = race_date
    self.race_title = race_title
    self.race_id = race_id
    self.start_at = start_at
    self.expires_at = expires_at
