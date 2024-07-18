from keiba_app import db
from datetime import datetime as dt

class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255))
  email = db.Column(db.String(255))
  is_premium = db.Column(db.Boolean)
  created_at = db.Column(db.DateTime, nullable=False, default=dt.now)  # 作成日時
  updated_at = db.Column(db.DateTime, nullable=False, default=dt.now, onupdate=dt.now)
