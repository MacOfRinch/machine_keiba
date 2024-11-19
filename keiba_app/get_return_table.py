# 未取得の払戻表を取得してDBに保存するプログラム
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import app, db
from models.race_calender import RaceCalenderModel
from models.race_result import RaceResultModel
from models.return_table import ReturnTableModel

from io import StringIO
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date as d
from dateutil import relativedelta
import random
from tqdm import tqdm
import time

with app.app_context():
  race_id_tupples = db.session.query(RaceResultModel.race_id).distinct().all()
  got_return_tables = db.session.query(ReturnTableModel.race_id).all()
got_result_ids = [race_id_tupple[0] for race_id_tupple in race_id_tupples]
got_return_ids = [got_return_id[0] for got_return_id in got_return_tables]
race_ids = []
for got_result_id in got_result_ids:
  if not got_result_id in got_return_ids:
    race_ids.append(got_result_id)

def scrape_return_table(race_id: str) -> pd.DataFrame:
  url = "https://db.netkeiba.com/race/" + race_id + "/"
  header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
  session = requests.Session()
  response = session.get(url, headers=header)
  response.encoding = 'EUC-JP'
  html = response.text
  html = html.replace('<br />', ', ')
  soup = BeautifulSoup(html, 'html.parser')
  tables = soup.find_all('table')

  return_table_1 = str(tables[1])
  return_table_2 = str(tables[2])
  df1 = pd.read_html(StringIO(return_table_1))[0]
  df2 = pd.read_html(StringIO(return_table_2))[0]
  df = pd.concat([df1, df2])
  df.columns = ['買い方', '馬番', '払戻単価', '人気']
  df.index = [race_id] * len(df)
  return df

def save_to_db(race_id: str, df: pd.DataFrame) -> None:
  data = {}
  for _, row in df.iterrows():
    if ', ' in row['払戻単価']:
      row['払戻単価'] = row['払戻単価'].split(', ')
      row['馬番'] = row['馬番'].split(', ')
      data[row['買い方']] = {key: value for key, value in zip(row['馬番'], row['払戻単価'])}
    else:
      data[row['買い方']] = {row['馬番']: row['払戻単価']}
  with app.app_context():
    return_table = ReturnTableModel(
      race_id=race_id,
      return_data=data
    )
    existing_race_id_tupples = db.session.query(ReturnTableModel.race_id).distinct().all()
    existing_race_ids = [race_id[0] for race_id in existing_race_id_tupples]
    if not return_table.race_id in existing_race_ids:
      db.session.add(return_table)
      db.session.commit()

if __name__ == '__main__':
  for race_id in tqdm(race_ids):
    try:
      df = scrape_return_table(race_id)
      save_to_db(race_id, df)
      time.sleep(random.randint(2, 5))
    except Exception as e:
      print(e)
      time.sleep(random.randint(2, 5))
      continue
