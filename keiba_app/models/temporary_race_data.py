from keiba_app import db

class TemporaryRaceData(db.Model):
  __tablename__ = 'temporary_race_data'
  id = db.Column(db.Integer, primary_key=True)
  race_id = db.Column(db.String(255), nullable=False)
  race_date = db.Column(db.String(255), nullable=False)
  start_at = db.Column(db.String(255))

  def __init__(self, race_id, race_date, start_at):
    self.race_id = race_id
    self.race_date = race_date
    self.start_at = start_at
