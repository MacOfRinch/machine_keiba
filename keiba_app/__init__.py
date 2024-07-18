from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('keiba_app.config')

db = SQLAlchemy(app)

import keiba_app.views
