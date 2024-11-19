from keiba_app import db

class PredictResultModel(db.Model):
  __tablename__ = 'predict_result'
  __table_args__ = {'extend_existing': True}
  id = db.Column(db.Integer, primary_key=True)
  race_title = db.Column(db.String(255), nullable=False)
  race_date = db.Column(db.String(255), nullable=False)
  race_id = db.Column(db.String(255), nullable=False)
  top_ratio = db.Column(db.Float)
  victory_ratio = db.Column(db.Float)
  box_ratio = db.Column(db.Float)
  recovery_rate = db.Column(db.Float)
  expires_at = db.Column(db.Date, nullable=False)

  def __init__(self, race_title, race_date, race_id, top_ratio, victory_ratio, box_ratio, recovery_rate, expires_at):
    self.race_title = race_title
    self.race_date = race_date
    self.race_id = race_id
    self.top_ratio = top_ratio
    self.victory_ratio = victory_ratio
    self.box_ratio = box_ratio
    self.recovery_rate = recovery_rate
    self.expires_at = expires_at
