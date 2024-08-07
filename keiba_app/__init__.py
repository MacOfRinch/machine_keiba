from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import joblib
import os

app = Flask(__name__)
app.config.from_object('keiba_app.config')
model = None
app.secret_key = os.getenv('SECRET_KEY')

def load_model():
  global model
  model = joblib.load('./keiba_app/trained_model/keiba_model.pkl')
  return model

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .models.race_result import RaceResultModel
from .models.horse import HorseModel
from .models.jockey import JockeyModel
from .logics.get_datum import UpdateDatum
from .logics.new_race import NewRace
from keiba_app import views
