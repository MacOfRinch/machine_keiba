# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# app = Flask(__name__)
# app.config.from_object('config')

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

from keiba_app import create_app, load_model, socketio
from keiba_app.scheduler_json import load_jobs_from_file

app = create_app()

if __name__ == '__main__':
  model = load_model()
  load_jobs_from_file()
  socketio.run(app, debug=False, port=8080)
