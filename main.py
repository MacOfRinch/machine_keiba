# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# app = Flask(__name__)
# app.config.from_object('config')

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

from keiba_app import app
from keiba_app import load_model

if __name__ == '__main__':
  load_model()
  app.run()
