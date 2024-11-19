from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import joblib
import os

app = Flask(__name__)
app.config.from_object('keiba_app.config')
# 暫定対応：ここはNoneで初期化してload_modelで読み込んだ値をviews.pyで使いたい
# model = None
model = joblib.load('./keiba_app/trained_model/keiba_model.pkl')
app.secret_key = os.getenv('SECRET_KEY')

def load_model():
  global model
  print(" * Loading pre-trained model ...")
  model = joblib.load('./keiba_app/trained_model/keiba_model.pkl')
  print(' * Loading end')
  return model

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .models.race_result import RaceResultModel
from .models.horse import HorseModel
from .models.jockey import JockeyModel
from .models.race_calender import RaceCalenderModel
from .models.predict_result import PredictResultModel
from .logics.get_datum import UpdateDatum
from .logics.new_race import NewRace
from .logics.predict_datum import PredictDatum
from .logics.odds_upper_limit import OddsUpperLimit
from keiba_app import views
