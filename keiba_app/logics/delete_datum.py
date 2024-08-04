# 毎週月曜日深夜に定期実行
# 期限切れのデータを削除しDBを空ける

from datetime import datetime as dt

from keiba_app import app, db
from ..models.race_result import RaceResultModel
from ..models.horse import HorseModel
from ..models.jockey import JockeyModel

class DeleteDatum:
  @staticmethod
  def delete_expired_datum():
    expired_race_datum = RaceResultModel.query.filter(dt.today() > RaceResultModel.expires_at).all()
    expired_horse_datum = HorseModel.query.filter(dt.today() > HorseModel.expires_at).all()
    expired_jockey_datum = JockeyModel.query.filter(dt.today() > JockeyModel.expires_at).all()
    with app.app_context():
      db.session.delete(expired_race_datum)
      db.session.delete(expired_horse_datum)
      db.session.delete(expired_jockey_datum)
