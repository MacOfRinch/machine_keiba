# coding: UTF-8
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from keiba_app import db
from flask import render_template, redirect, url_for, flash, jsonify, Blueprint
from flask import request, session
from flask import g
import time
from datetime import datetime as dt
from datetime import date as d
from dateutil.relativedelta import relativedelta
import random

from keiba_app.models.race_result import RaceResultModel
from keiba_app.models.race_calender import RaceCalenderModel
from keiba_app.models.predict_result import PredictResultModel
from keiba_app.logics.get_datum import UpdateDatum
from keiba_app.logics.new_race import NewRace
from keiba_app.logics.predict_datum import PredictDatum
from keiba_app import scheduler
from keiba_app.scheduler_json import save_jobs_to_file
from keiba_app.scheduled_jobs import *

bp = Blueprint('views', __name__)

@bp.route('/')
def main_display():
  # 近レースの予想と今までの的中率・回収率、おすすめの賭け方を提示するページ
  scheduled_race_data = db.session.query(RaceCalenderModel).all()
  future_race_ids = []
  for scheduled_race in scheduled_race_data:
    date = scheduled_race.race_date
    if dt.strptime(date, '%Y%m%d') >= dt.now():
      future_race_ids.append(scheduled_race.race_id)
  race_predictions = []
  return_tables = []
  updated_at = f'最終更新: {dt.now().strftime("%m/%d %H:%M:%S")}'
  if bool(future_race_ids):
    race_predictions = [PredictDatum.predict(race_id)['data'] for race_id in future_race_ids]
    return_tables = [PredictDatum.predict(race_id)['return'] for race_id in future_race_ids]
    return render_template('keiba_app/main_display.html', data_tables=race_predictions, return_tables=return_tables, updated_at=updated_at)
  else:
    # races = db.session.query(RaceResultModel).filter(RaceResultModel.race_date == '20241201').all()
    # selected_race = random.choice(races)
    # from keiba_app.scheduled_jobs import test
    # selected_race = test()
    # prediction = PredictDatum.predict(selected_race.race_id)['data']
    return render_template('keiba_app/no_races.html')

@bp.route('/races')
def index():
  # 過去のレースのデータ一覧
  race_data = db.session.query(RaceResultModel.race_id, RaceResultModel.race_date, RaceResultModel.predict_flag).distinct().order_by(RaceResultModel.race_date.desc()).all()
  predict_results = db.session.query(PredictResultModel).all()
  return render_template('keiba_app/index.html', race_data=race_data)

@bp.route('/race/<string:race_id>')
def show_race_detail(race_id):
  race_data = RaceResultModel.query.filter(RaceResultModel.race_id == race_id)
  return render_template('/keiba_app/show_race.html', race_data=race_data)

# 基本的に表示しない、未取得のレースデータが載ったページ
@bp.route('/race/get_datum')
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
# 月曜10:00にはまだ更新なし
@bp.route('/race/get_datum/<string:race_date>', methods=['POST'])
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
          from main import app
          horse_and_jockey_dict = UpdateDatum.get_race_data(race_id, app)
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
        try:
          from main import app
          UpdateDatum.get_horse_data(horse_id, date, app)
          print(f'馬id{horse_id}のデータ取得完了')
          time.sleep(3)
        except Exception as e:
          print(e)
          break
      for jockey_id in unique_jockey_ids:
        from main import app
        UpdateDatum.get_jockey_data(jockey_id, app)
        print(f'騎手id{jockey_id}のデータ取得完了')
        time.sleep(3)
      session['message'] = 'データの取得が正常に完了しました'
    except Exception as e:
      print(e)
      session['message'] = 'データの取得に失敗しました'
      time.sleep(3)
    flash(session['message'])
  return redirect(url_for('views.race_date_index'))

# 新しいレースのある日付を表示(暫定　カレンダーにする予定)
@bp.route('/new_races/index')
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

@bp.route('/new_races/index/<string:race_date>', methods=['GET'])
def new_race_id_index(race_date: str):
  session.pop('message', None)
  # race_infomations = NewRace.get_new_race_infomations(race_date)
  race_infomations = RaceCalenderModel.query.filter(RaceCalenderModel.race_date == race_date).all()
  date = dt.strptime(race_date, '%Y%m%d')
  date = dt.strftime(date, '%Y年%m月%d日')
  return render_template('keiba_app/new_race_index.html', race_infomations=race_infomations, race_date=date)

@bp.route('/new_races/show/<string:race_id>', methods=['GET'])
def show_new_race(race_id: str):
  # 現在のコードはページリクエスト時に都度スクレイピング∴レス遅い　本番ではレースのある日に5分ごとに定期実行した結果をjsでリアルタイム表示する
  race_ids = [race_id_tupple[0] for race_id_tupple in db.session.query(RaceCalenderModel.race_id).all()]
  if race_id not in race_ids:
    return render_template('keiba_app/no_race.html', race_id=race_id)
  session.pop('message', None)
  new_race_datum = NewRace.scrape(race_id)
  race_info = RaceCalenderModel.query.filter(RaceCalenderModel.race_id == race_id).first()
  race_date = race_info.race_date
  feature = NewRace.analyze(race_date, new_race_datum['race_df'])
  from keiba_app import model
  prediction = model.predict(feature).tolist()
  predict_datum = new_race_datum['race_df']
  predict_datum['競走力指数'] = [x * 100 / sum(prediction) for x in prediction]
  # 暫定　表示が少し変
  col = [('枠', '枠'), ('馬番', '馬番'), ('馬名', '馬名'), ('騎手', '騎手'), ('オッズ', 'オッズ'), ('競走力指数', '')]
  display_data = predict_datum[col]
  temporary_return_table = new_race_datum['odds_df']
  df = new_race_datum['race_df']
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
@bp.route('/api/predict/<string:race_id>', methods=['POST'])
def predict(race_id: str):
  response = {
    'success': False,
    'Content-Type': 'application/json'
  }
  if request.method == 'POST':
    if request.get_json().get('race_id'):
      race_data = NewRace.scrape(race_id)
      feature = NewRace.analyze(race_data)
      from keiba_app import model
      response['prediction'] = model.predict(feature).to_list()
      response['success'] = True
  return jsonify(response)

# 定期実行スケジュールを変更するためのリクエスト
# viewではないが、便宜上ここに置く
@bp.route('/schedule/update_job', methods=['POST'])
def update_job():
  response = {
    'success': False,
    'Content-Type': 'application/json',
    'message': None
  }
  # if request.method == 'POST':
  # scheduler.remove_job('default_job')
  # scheduler.add_job(
  #   id='default_job_1',
  #   func=default_job,
  #   trigger='cron',
  #   minute='*/1'
  # )
  this_month = dt.today().month
  days_for_cron = get_days_of_race_held()
  
  jobs = scheduler.get_jobs()
  for job in jobs:
    if job.id == 'get_days_of_race_held':
      scheduler.remove_job('get_days_of_race_held')
  scheduler.add_job(
    id='get_days_of_race_held',
    func=get_days_of_race_held,
    trigger='cron',
    hour='1',
    minute='0',
    second='0'
  )
  response['success'] = True
  response['message'] = 'ジョブの更新に成功しました！'
  jobs = scheduler.get_jobs()
  for job in jobs:
    print(f"Job ID: {job.id}, Next run time: {job.next_run_time}")
  save_jobs_to_file(scheduler)
  return jsonify(response)

@bp.route('/check_scheduled_jobs', methods=['POST'])
def check_scheduled_jobs():
  jobs = scheduler.get_jobs()
  for job in jobs:
    print(f"Job ID: {job.id}, Next run time: {job.next_run_time}")
  return redirect(url_for('views.hello'))

@bp.route('/hello', methods=['GET'])
def hello():
  return render_template('keiba_app/hello.html')
