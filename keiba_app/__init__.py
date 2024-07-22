from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('keiba_app.config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .models.race_result import RaceResultModel
from keiba_app import views
