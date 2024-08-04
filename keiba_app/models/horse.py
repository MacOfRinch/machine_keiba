from keiba_app import db
# from ..logics.get_datum import half_year_later

class HorseModel(db.Model):
  __tablename__ = 'horse'
  id = db.Column(db.Integer, primary_key=True)
  horse_id = db.Column(db.String(255), unique=True)
  order_ave = db.Column(db.Float)
  expires_at = db.Column(db.Date, nullable=False)

  def __init__(self, horse_id, order_ave, expires_at):
    self.horse_id = horse_id
    self.order_ave = order_ave
    self.expires_at = expires_at
