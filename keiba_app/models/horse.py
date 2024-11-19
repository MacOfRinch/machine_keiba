from keiba_app import db
import json
# from ..logics.get_datum import half_year_later

class HorseModel(db.Model):
  __tablename__ = 'horse'
  __table_args__ = {'extend_existing': True}
  id = db.Column(db.Integer, primary_key=True)
  horse_id = db.Column(db.String(255), unique=True)
  order_ave_info = db.Column(db.JSON)
  expires_at = db.Column(db.Date, nullable=False)

  def __init__(self, horse_id, order_ave_info, expires_at):
    self.horse_id = horse_id
    self.order_ave_info = order_ave_info
    self.expires_at = expires_at
