# 毎週月曜日深夜に定期実行
# 期限切れのデータを削除しDBを空ける

from datetime import datetime as dt

from keiba_app import db
from ..models.services import RaceResultModel
from ..models.services import HorseModel
from ..models.services import JockeyModel

class DeleteDatum:
  @staticmethod
  def delete_expired_datum():
    expired_race_datum = RaceResultModel.query.filter(dt.today() > RaceResultModel.expires_at).all()
    expired_horse_datum = HorseModel.query.filter(dt.today() > HorseModel.expires_at).all()
    expired_jockey_datum = JockeyModel.query.filter(dt.today() > JockeyModel.expires_at).all()
    from main import app
    with app.app_context():
      db.session.delete(expired_race_datum)
      db.session.delete(expired_horse_datum)
      db.session.delete(expired_jockey_datum)
      db.session.commit()
