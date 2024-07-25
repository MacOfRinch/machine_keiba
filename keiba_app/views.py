# coding: UTF-8
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import app
from keiba_app import db
from flask import render_template
from flask import request
from keiba_app import RaceResultModel

@app.route('/')
def index():
  race_data = db.session.query(RaceResultModel.race_id, RaceResultModel.race_date).distinct().order_by(RaceResultModel.race_date.desc()).all()
  return render_template('keiba_app/index.html', race_data=race_data)

@app.route('/race/<int:race_id>')
def show_race_detail(race_id):
  race_data = RaceResultModel.query.filter(RaceResultModel.race_id == race_id)
  return render_template('/keiba_app/show_race.html', race_data=race_data)
