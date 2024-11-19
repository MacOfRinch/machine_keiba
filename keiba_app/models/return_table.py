from keiba_app import db
# from ..logics.get_datum import half_year_later

class ReturnTableModel(db.Model):
  __tablename__ = 'return_table'
  id = db.Column(db.Integer, primary_key=True)
  race_id = db.Column(db.String(255), nullable=False)
  return_data = db.Column(db.JSON)

  def __init__(self, race_id, return_data):
    self.race_id = race_id
    self.return_data = return_data

