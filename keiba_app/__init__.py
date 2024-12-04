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
  model = None
  app.secret_key = os.getenv('SECRET_KEY')

  db.init_app(app)
  migrate.init_app(app, db)
  # 本番ではcorsきっちりやる
  socketio.init_app(app, cors_allowed_origins="*")
  if not scheduler.running:
    print("Scheduler is starting...")
    scheduler.init_app(app)
    scheduler.start()
  # 初期登録スケジューラ
  # with app.app_context():
  #   from keiba_app.scheduled_jobs import default_job
  #   scheduler.add_job(
  #   id='default_job',
  #   func=default_job,
  #   trigger='cron',
  #   minute='*/2'
  # )
  if model == None:
    @app.before_request
    def setup_model():
      g.model = load_model()

  with app.app_context():
    from keiba_app import views
    app.register_blueprint(views.bp)
  return app

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
