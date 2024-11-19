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
from keiba_app import RaceCalenderModel
from keiba_app import PredictResultModel
from keiba_app import UpdateDatum
from keiba_app import NewRace
from keiba_app import PredictDatum
from keiba_app import OddsUpperLimit

@app.route('/')
def main_display():
  # 近レースの予想と今までの的中率・回収率、おすすめの賭け方を提示するページ
  race_id = '202405040501'
  predict = PredictDatum.predict(race_id)['data']
  return_table = PredictDatum.predict(race_id)['return']
  return render_template('keiba_app/main_display.html', table=predict.to_html(classes='table table-striped'), return_table=return_table.to_html(classes='table table-striped'))

@app.route('/races')
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
  got_race_dates = db.session.query(RaceResultModel.race_date).distinct().all()
  scheduled_race_dates = db.session.query(RaceCalenderModel.race_date).distinct().all()
  got_race_dates = [d.strftime(date[0], '%Y%m%d') for date in got_race_dates]
  display_race_dates = []
  for date in scheduled_race_dates:
    if not date[0] in got_race_dates:
      display_race_dates.append(date[0])
  display_race_dates = [str(date) for date in display_race_dates]
  return render_template('/keiba_app/race_dates_index.html', race_dates=display_race_dates)

# 基本的に手動では実行しない、未取得の過去のレースデータを取得するリクエスト
@app.route('/race/get_datum/<string:race_date>', methods=['POST'])
def get_new_datum(race_date):
  if request.method == 'POST':
    session.pop('message', None)
    try:
      str_date = str(race_date)
      date = dt.strptime(race_date, '%Y%m%d').date()
      # 30分くらいかかる処理
      race_infomations = RaceCalenderModel.query.filter(RaceCalenderModel.race_date == str_date).all()
      race_ids = [race_infomation.race_id for race_infomation in race_infomations]
      all_horse_ids = []
      all_jockey_ids = []
      for race_id in race_ids:
        try:
          horse_and_jockey_dict = UpdateDatum.get_race_data(race_id)
          horse_ids = horse_and_jockey_dict['horse_id_list']
          jockey_ids = horse_and_jockey_dict['jockey_id_list']
          all_horse_ids += horse_ids
          all_jockey_ids += jockey_ids
          print(f'レースid{race_id}のデータ取得完了')
          time.sleep(3)
        except Exception as e:
          print(e)
          time.sleep(3)
          continue
      unique_horse_ids = list(set(all_horse_ids))
      unique_jockey_ids = list(set(all_jockey_ids))
      for horse_id in unique_horse_ids:
        UpdateDatum.get_horse_data(horse_id, date)
        print(f'馬id{horse_id}のデータ取得完了')
        time.sleep(3)
      for jockey_id in unique_jockey_ids:
        UpdateDatum.get_jockey_data(jockey_id)
        print(f'騎手id{jockey_id}のデータ取得完了')
        time.sleep(3)
      session['message'] = 'データの取得が正常に完了しました'
    except Exception as e:
      print(e)
      session['message'] = 'データの取得に失敗しました'
      time.sleep(3)
    flash(session['message'])
  return redirect(url_for('race_date_index'))

# 新しいレースのある日付を表示(暫定　カレンダーにする予定)
@app.route('/new_races/index')
def new_race_date_index():
  got_race_dates = db.session.query(RaceResultModel.race_date).distinct().all()
  scheduled_race_dates = db.session.query(RaceCalenderModel.race_date).distinct().all()
  got_race_dates = [d.strftime(date[0], '%Y%m%d') for date in got_race_dates]
  display_race_dates = []
  for date in scheduled_race_dates:
    if not date[0] in got_race_dates:
      display_race_dates.append(date[0])
  race_dates = [date for date in display_race_dates]
  if bool(race_dates):
    return render_template('keiba_app/new_race_dates_index.html', race_dates=race_dates)
  else:
    return render_template('keiba_app/no_races.html')

@app.route('/new_races/index/<string:race_date>', methods=['GET'])
def new_race_id_index(race_date: str):
  session.pop('message', None)
  # race_infomations = NewRace.get_new_race_infomations(race_date)
  race_infomations = RaceCalenderModel.query.filter(RaceCalenderModel.race_date == race_date).all()
  date = dt.strptime(race_date, '%Y%m%d')
  date = dt.strftime(date, '%Y年%m月%d日')
  return render_template('keiba_app/new_race_index.html', race_infomations=race_infomations, race_date=date)

@app.route('/new_races/show/<string:race_id>', methods=['GET'])
def show_new_race(race_id: str):
  session.pop('message', None)
  new_race_datum = NewRace.scrape(race_id)
  race_info = RaceCalenderModel.query.filter(RaceCalenderModel.race_id == race_id).first()
  race_date = race_info.race_date
  feature = NewRace.analyze(race_date, new_race_datum[0])
  prediction = model.predict(feature).tolist()
  predict_datum = new_race_datum[0]
  predict_datum['スコア'] = prediction
  # 暫定　表示が少し変
  col = [('枠', '枠'), ('馬番', '馬番'), ('馬名', '馬名'), ('騎手', '騎手'), ('オッズ', 'オッズ'), ('スコア', '')]
  display_data = predict_datum[col]
  temporary_return_table = new_race_datum[1]
  df = new_race_datum[0]
  if df['predict_flag'].all():
    session['message'] = '現時点での情報です。レースが近づくと変わる可能性があります。'
    flash(session['message'])
  else:
    session['message'] = 'データ不足のため予測精度が十分ではありません'
    flash(session['message'])
  return render_template('keiba_app/new_race_show.html', race_id=race_id, table=display_data.to_html(classes='table table-striped'), return_table=temporary_return_table)

# 効率的なオッズリミットを計算するための開発時用ページ
# @app.route('/fukushou')
# def kaishu():
#   OddsUpperLimit.calc_fukushou()
#   return None

# @app.route('/wide')
# def kaishu_wide():
#   OddsUpperLimit.calc_wide()
#   return None

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
