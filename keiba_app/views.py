# coding: UTF-8
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from keiba_app import app, db, model
from flask import render_template, redirect, url_for, flash, jsonify
from flask import request, session
import time
from datetime import datetime as dt
from datetime import date as d
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
  half_year_ago = d.today() + relativedelta(months=-6)
  day = half_year_ago
  got_race_dates = db.session.query(RaceResultModel.race_date).distinct().all()
  race_dates = []
  while day < d.today():
    if (day.weekday() == 5) or (day.weekday() == 6):
      if (day, ) not in got_race_dates:
        race_dates.append(day)
    day += relativedelta(days=1)
  race_dates = [d.strftime(date, '%Y%m%d') for date in race_dates]
  return render_template('/keiba_app/race_dates_index.html', race_dates=race_dates)

# 基本的に手動では実行しない、未取得の過去のレースデータを取得するリクエスト
@app.route('/race/get_datum/<int:date>', methods=['POST'])
def get_new_datum(date):
  if request.method == 'POST':
    session.pop('message', None)
    try:
      str_date = str(date)
      # 時間かかる処理
      race_ids = NewRace.get_new_race_infomations(str_date)
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

# 新しいレースのある日付を表示(暫定　カレンダーにする予定)
@app.route('/new_races/index')
def new_race_date_index():
  got_race_dates = db.session.query(RaceResultModel.race_date).distinct().all()
  day = d.today() + relativedelta(months=-2)
  race_dates = []
  while day < d.today() + relativedelta(days=3):
    if (day.weekday() == 5) or (day.weekday() == 6):
      if (day, ) not in got_race_dates:
        race_dates.append(day)
    day += relativedelta(days=1)
  race_dates = [d.strftime(date, '%Y%m%d') for date in race_dates]
  return render_template('keiba_app/new_race_dates_index.html', race_dates=race_dates)

@app.route('/new_races/index/<string:race_date>', methods=['GET'])
def new_race_id_index(race_date: str):
  session.pop('message', None)
  race_infomations = NewRace.get_new_race_infomations(race_date)
  date = dt.strptime(race_date, '%Y%m%d')
  date = dt.strftime(date, '%Y年%m月%d日')
  return render_template('keiba_app/new_race_index.html', race_infomations=race_infomations, race_date=date)

@app.route('/new_races/show/<string:race_id>', methods=['GET'])
def show_new_race(race_id: str):
  session.pop('message', None)
  session['message'] = '現時点での情報です。レースが近づくと変わる可能性があります。'
  flash(session['message'])
  new_race_data = NewRace.scrape(race_id)
  # 暫定　表示が少し変
  col = [('枠', '枠'), ('馬番', '馬番'), ('馬名', '馬名'), ('騎手', '騎手'), ('オッズ', 'オッズ')]
  display_data = new_race_data[col]
  return render_template('keiba_app/new_race_show.html', race_id=race_id, table=display_data.to_html(classes='table table-striped'))

# 結果予想API
@app.route('/api/predict/<string:race_id>', methods=['POST'])
def predict(race_id: str):
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
  return jsonify(response)
