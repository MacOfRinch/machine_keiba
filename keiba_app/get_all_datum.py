# 未取得のレースデータと馬・騎手データをスクレイピングしてDBに保存するプログラム
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from keiba_app import db
from datetime import date as d
from datetime import datetime as dt
import datetime
import requests
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import time
from io import StringIO
from tqdm import tqdm
import random
from sqlalchemy.orm.attributes import flag_modified
from models.horse import HorseModel
from models.jockey import JockeyModel
from models.race_result import RaceResultModel
from models.race_calender import RaceCalenderModel
from models.predict_result import PredictResultModel

# あとで直す
date = dt.strptime('2024-11-23', '%Y-%m-%d').date()
this_year = int(dt.today().year)
half_year_later = date + relativedelta(months=6)
# ここも直す
with app.app_context():
  race_infomations = RaceCalenderModel.query.filter(RaceCalenderModel.race_date == '20241123').all()
race_ids = [race_infomation.race_id for race_infomation in race_infomations]

all_horse_ids = []
all_jockey_ids = []

for race_id in race_ids:
  try:
    url = "https://db.netkeiba.com/race/" + race_id + "/"
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    session = requests.Session()
    response = session.get(url, headers=header)
    response.encoding = "EUC-JP"

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all('table')
    data_table = str(tables[0])
    df = pd.read_html(StringIO(data_table))[0]
    # 半角スペースがあったら除去
    df = df.rename(columns=lambda x: x.replace(' ', ''))
    all_horse_ids = []
    horse_id_list = []
    jockey_id_list = []

    horse_link_list = soup.find('table', attrs={'summary': 'レース結果'}).find_all('a', attrs={'href': re.compile(r'^/horse/')})
    for horse_link in horse_link_list:
      horse_id = ''.join(re.findall(r'\d+', horse_link['href']))
      horse_id_list.append(horse_id)
    all_horse_ids += horse_id_list
    jockey_link_list = soup.find('table', attrs={'summary': 'レース結果'}).find_all('a', attrs={'href': re.compile(r'^/jockey/result/recent/')})
    for jockey_link in jockey_link_list:
      jockey_id = ''.join(re.findall(r'\d+', jockey_link['href']))
      jockey_id_list.append(jockey_id)
    all_jockey_ids += jockey_id_list
    time.sleep(3)
  except Exception as e:
    print(e)
    print(race_id)
    time.sleep(3)
    continue

unique_horse_ids = list(set(all_horse_ids))
unique_jockey_ids = list(set(all_jockey_ids))

for horse_id in unique_horse_ids:
  horse_url = 'https://db.netkeiba.com/horse/' + horse_id + '/'
  try:
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    session = requests.Session()
    response = session.get(horse_url, headers=header)
    response.encoding = 'EUC-JP'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    target_table = soup.find('table', attrs={'class': 'db_h_race_results'})
    str_table = str(target_table)
    df = pd.read_html(StringIO(str_table))[0]
    df = df.rename(columns=lambda x: x.replace(' ', ''))

    df.index = [horse_id] * len(df)
    df['日付'] = df['日付'].apply(lambda x: dt.strptime(x, '%Y/%m/%d'))
    df = df.loc[df['日付'] >= (dt.today() + relativedelta(months=-6))]
    rows = []
    for _, row in df.iterrows():
      try:
        rows.append(int(row['着順']) / int(row['頭数']))
      except ValueError:
        continue
      except KeyError:
        continue
    try:
      order_ave = sum(rows) / len(rows)
    except ZeroDivisionError:
      order_ave = None
    with app.app_context():
      horse_id_list = [horse_id[0] for horse_id in db.session.query(HorseModel.horse_id).all()]
      horse_info = db.session.query(HorseModel).filter(HorseModel.horse_id == horse_id).first()
      if bool(horse_info):
        # 日付を文字列化してそのデータを追加
        order_ave_data = horse_info.order_ave_info
        order_ave_data[str(date)] = order_ave
        horse_info.order_ave_info = order_ave_data
        flag_modified(horse_info, 'order_ave_info')
        horse_info.expires_at = date + relativedelta(months=6)
      elif horse_id not in horse_id_list:
        order_ave_data = {}
        order_ave_data[str(date)] = order_ave
        horse_data = HorseModel(
          horse_id=horse_id,
          order_ave_info=order_ave_data,
          expires_at=date+relativedelta(months=6)
        )
        db.session.add(horse_data)
      else:
        print('何かがおかしい')
      db.session.commit()
      # データ更新確認用
      print(f'{horse_id}: {horse_info.order_ave_info}')
    time.sleep(3)
  except Exception as e:
    print(e)
    print(horse_id)
    time.sleep(3)

for jockey_id in unique_jockey_ids:
  jockey_url = 'https://db.netkeiba.com/jockey/result/' + jockey_id + '/'
  try:
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    session = requests.Session()
    response = session.get(jockey_url, headers=header)
    response.encoding = 'EUC-JP'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    target_table = soup.find('table', attrs={'summary': '年度別成績'})
    jockey_table = str(target_table)
    df = pd.read_html(StringIO(jockey_table))[0]
    text = soup.select('div.db_head_name p')[0].text
    birth_year = int(re.findall(r'\d+', text)[0])
    old = this_year - birth_year
    top_count = []
    victory_count = []
    runs = []
    years = [str(this_year - 2), str(this_year - 1), str(this_year)]
    for _, row in df.iterrows():
      if row['年度']['年度'] in years:
        top_count.append(int(row['1着']['1着']))
        victory_count.append(int(row['1着']['1着']) + int(row['2着']['2着']) + int(row['3着']['3着']))
        runs.append(int(row['1着']['1着']) + int(row['2着']['2着']) + int(row['3着']['3着']) + int(row['着外']['着外']))
    top_ratio = sum(top_count) / sum(runs)
    victory_ratio = sum(victory_count) / sum(runs)
    experience = sum(runs)
    with app.app_context():
      ockey_id_list = [jockey_id[0] for jockey_id in db.session.query(JockeyModel.jockey_id).all()]
      jockey_info = db.session.query(JockeyModel).filter(JockeyModel.jockey_id == jockey_id).first()
      if bool(jockey_info):
        jockey_info.old = old
        jockey_info.top_ratio = top_ratio
        jockey_info.victory_ratio = victory_ratio
        jockey_info.experience = experience
        jockey_info.expires_at = half_year_later
      elif jockey_id not in jockey_id_list:
        jockey_data = JockeyModel(
          jockey_id=jockey_id,
          old=old,
          top_ratio=top_ratio,
          victory_ratio=victory_ratio,
          experience=experience,
          expires_at=half_year_later
        )
        db.session.add(jockey_data)
      else:
        print('jockeyが何かおかしい')
      db.session.commit()
    time.sleep(3)
  except Exception as e:
    print(e)
    print(jockey_id)
    time.sleep(3)
    continue

#   for key, value in horse.order_ave_info.items():
#     print(f'{key}: {value}')
