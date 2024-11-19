from keiba_app import db
# from ..logics.get_datum import half_year_later

class JockeyModel(db.Model):
  __tablename__ = 'jockey'
  __table_args__ = {'extend_existing': True}
  id = db.Column(db.Integer, primary_key=True)
  jockey_id = db.Column(db.String(255), unique=True)
  old = db.Column(db.Integer)
  top_ratio = db.Column(db.Float)
  victory_ratio = db.Column(db.Float)
  experience = db.Column(db.Integer)
  expires_at = db.Column(db.Date, nullable=False)

  def __init__(self, jockey_id, old, top_ratio, victory_ratio, experience, expires_at):
    self.jockey_id = jockey_id
    self.old = old
    self.top_ratio = top_ratio
    self.victory_ratio = victory_ratio
    self.experience = experience
    self.expires_at = expires_at
