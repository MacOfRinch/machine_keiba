import eventlet
eventlet.monkey_patch()

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
from pytz import timezone
import joblib
import os

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
socketio = SocketIO()

def create_app():
  app = Flask(__name__)
  app.config.from_object('keiba_app.config')
  # model = None
  app.secret_key = os.getenv('SECRET_KEY')

  db.init_app(app)
  migrate.init_app(app, db)
  if not scheduler.running:
    print("Scheduler is starting...")
    scheduler.init_app(app)
    scheduler.start()

  # if model == None:
  #   @app.before_request
  #   def setup_model():
  #     g.model = load_model()

  with app.app_context():
    from keiba_app import views, web_sockets, web_sockets_hello
    app.register_blueprint(views.bp)
  return app

model = None

def load_model():
  global model
  print(" * Loading pre-trained model ...")
  model = joblib.load('./keiba_app/trained_model/keiba_model.pkl')
  print(' * Loading end')
  return model

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# scheduler.init_app(app)

# from .logics.get_datum import UpdateDatum
# from .logics.new_race import NewRace
# from .logics.predict_datum import PredictDatum
# from .logics.odds_upper_limit import OddsUpperLimit
# from keiba_app import views
