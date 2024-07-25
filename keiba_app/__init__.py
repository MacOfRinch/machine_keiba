from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import joblib

app = Flask(__name__)
app.config.from_object('keiba_app.config')
model = None

def load_model():
  global model
  model = joblib.load('./keiba_app/trained_model/keiba_model.pkl')
  return model

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .models.race_result import RaceResultModel
from .models.horse import HorseModel
from .models.jockey import JockeyModel
from keiba_app import views
