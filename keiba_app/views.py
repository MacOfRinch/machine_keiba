# coding: UTF-8
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from keiba_app import app, db, model
from flask import render_template, redirect, url_for, flash
from flask import request, session
import time
from datetime import date as dt
from dateutil.relativedelta import relativedelta
from keiba_app import RaceResultModel
from keiba_app import UpdateDatum
from keiba_app import NewRace

@app.route('/')
def index():
  race_data = db.session.query(RaceResultModel.race_id, RaceResultModel.race_date).distinct().order_by(RaceResultModel.race_date.desc()).all()
  return render_template('keiba_app/index.html', race_data=race_data)

@app.route('/race/<int:race_id>')
def show_race_detail(race_id):
  race_data = RaceResultModel.query.filter(RaceResultModel.race_id == race_id)
  return render_template('/keiba_app/show_race.html', race_data=race_data)

# 基本的に表示しない、未取得のレースデータが載ったページ
@app.route('/race/get_datum')
def race_date_index():
  half_year_ago = dt.today() + relativedelta(months=-6)
  day = half_year_ago
  got_race_dates = db.session.query(RaceResultModel.race_date).distinct().all()
  race_dates = []
  while day < dt.today():
    if (day.weekday() == 5) or (day.weekday() == 6):
      if (day, ) not in got_race_dates:
        race_dates.append(day)
    day += relativedelta(days=1)
  race_dates = [dt.strftime(date, '%Y%m%d') for date in race_dates]
  return render_template('/keiba_app/race_dates_index.html', race_dates=race_dates)

# 基本的に手動では実行しない、未取得の過去のレースデータを取得するリクエスト
@app.route('/race/get_datum/<int:date>', methods=['POST'])
def get_new_datum(date):
  if request.method == 'POST':
    session.pop('message', None)
    try:
      str_date = str(date)
      # 時間かかる処理
      race_ids = NewRace.get_new_race_ids(str_date)
      all_horse_ids = []
      all_jockey_ids = []
      for race_id in race_ids:
        horse_and_jockey_dict = UpdateDatum.get_race_data(race_id)
        horse_ids = horse_and_jockey_dict['horse_id_list']
        jockey_ids = horse_and_jockey_dict['jockey_id_list']
        all_horse_ids += horse_ids
        all_jockey_ids += jockey_ids
        time.sleep(1)
      unique_horse_ids = list(set(all_horse_ids))
      unique_jockey_ids = list(set(all_jockey_ids))
      for horse_id in unique_horse_ids:
        UpdateDatum.get_horse_data(horse_id)
        time.sleep(1)
      for jockey_id in unique_jockey_ids:
        UpdateDatum.get_jockey_data(jockey_id)
        time.sleep(1)
      session['message'] = 'データの取得が正常に完了しました'
    except Exception as e:
      print(e)
      session['message'] = 'データの取得に失敗しました'
    flash(session['message'])
  return redirect(url_for('race_date_index'))

@app.route('/api/predict/<int:race_id>', methods=['POST'])
def predict(race_id):
  response = {
    'success': False,
    'Content-Type': 'application/json'
  }
  if request.method == 'POST':
    if request.get_json().get('race_id'):
      race_data = NewRace.scrape(race_id)
      feature = NewRace.analyze(race_data)
      response['prediction'] = model.predict(feature).to_list()
      response['success'] = True
  return response
