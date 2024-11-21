# 新しいレース情報が出たらスクレイピングし、分析に用いる準備をする
# 実際に分析を行い表示するのはviews.py

from keiba_app import app, db
from ..models.horse import HorseModel
from ..models.jockey import JockeyModel
from ..models.race_calender import RaceCalenderModel
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm import sessionmaker
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import re
from selenium import webdriver
from datetime import datetime as dt
import time

class NewRace:
  @staticmethod
  def get_new_race_infomations(date: str) -> None:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    url = 'https://race.netkeiba.com/top/?kaisai_date=' + date
    driver.get(url)
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    infomations = []
    link_list = soup.find('div', attrs={'class': 'RaceList_Box'}).find_all('a', attrs={'href': re.compile(r'^../race/(shutuba|result)\.html')})
    for link in link_list:
      title = link.select('span.ItemTitle')[0].text
      race_id = ''.join(re.findall(r'\d+', link['href']))
      infomations.append({'title': title, 'race_id': race_id})
    # 取得した情報をrace_calenderテーブルに保存
    dates_list = db.session.query(RaceCalenderModel.race_date).all()
    with app.app_context():
      for infomation in infomations:
        new_race_data = RaceCalenderModel(
          race_title=infomation['title'],
          race_date=date,
          race_id=infomation['race_id'],
          expires_at=date+relativedelta(months=6)
        )
        if not new_race_data.race_date in dates_list:
          db.session.add(new_race_data)
      db.session.commit()

  @staticmethod
  def scrape(new_race_id: str) -> dict:
    race_url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + new_race_id
    odds_url = 'https://race.netkeiba.com/odds/index.html?race_id=' + new_race_id
    # try:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    # 出馬表を取得
    driver.get(race_url)
    time.sleep(3)
    race_html = driver.page_source
    race_soup = BeautifulSoup(race_html, 'html.parser')
    # オッズのページ内容を取得
    driver.get(odds_url)
    time.sleep(3)
    odds_html = driver.page_source
    odds_soup = BeautifulSoup(odds_html, 'html.parser')

    main_text = race_soup.select('div.RaceList_Item02 h1')[0].text
    predict_flag = True
    if ('新馬' in main_text) or ('未出走' in main_text):
      predict_flag = False
    shutuba_table = race_soup.find('table', attrs={'class': 'Shutuba_Table'})
    str_race_table = str(shutuba_table)
    race_df = pd.read_html(StringIO(str_race_table))[0]
    race_df = race_df.rename(columns=lambda x: x.replace(' ', ''))
    # 確認用 後で消すよ
    print(race_df)
    horse_id_list = []
    jockey_id_list = []
    horse_link_list = race_soup.find('table', attrs={'class': 'Shutuba_Table'}).find_all('a', attrs={'href': re.compile(r'^https://db.netkeiba.com/horse/\d+')})
    for horse_link in horse_link_list:
      horse_id = ''.join(re.findall(r'\d+', horse_link['href']))
      horse_id_list.append(horse_id)
        
    jockey_link_list = race_soup.find('table', attrs={'class': 'Shutuba_Table'}).find_all('a', attrs={'href': re.compile(r'^https://db.netkeiba.com/jockey/result/recent/\d+')})
    for jockey_link in jockey_link_list:
      jockey_id = ''.join(re.findall(r'\d+', jockey_link['href']))
      jockey_id_list.append(jockey_id)

    race_df['horse_id'] = horse_id_list
    race_df['jockey_id'] = jockey_id_list
    got_horse_ids = [horse_id[0] for horse_id in db.session.query(HorseModel.horse_id).all()]
    for horse_id in horse_id_list:
      if not horse_id in got_horse_ids:
        print('馬データが足らないよ！')
        predict_flag = False
    got_jockey_ids = [jockey_id[0] for jockey_id in db.session.query(JockeyModel.jockey_id).all()]
    for jockey_id in jockey_id_list:
      if not jockey_id in got_jockey_ids:
        print('騎手のデータが足らないよ！')
        predict_flag = False
    race_df['predict_flag'] = [predict_flag] * len(race_df)

    # 現時点では単勝・複勝のみ
    odds_table = odds_soup.find('table', attrs={'class': 'RaceOdds_HorseList_Table', 'id': 'Ninki'})
    str_odds_table = str(odds_table)
    odds_df = pd.read_html(StringIO(str_odds_table))
    odds_df = odds_df.rename(columns=lambda x: x.replace(' ', ''))
    # 確認用 あとで消すよ
    print(odds_df)
    # except Exception as e:
    #   print(e)
    #   return
    updated_at = dt.now().strftime('%m/%d %H:%M:%S')
    return {'race_df': race_df, 'odds_df': odds_df, 'updated_at': updated_at}
  
  @staticmethod
  def analyze(race_date: str, df: pd.DataFrame) -> pd.DataFrame | None:
    """
    scrapeで集めたレースデータが新馬など予想困難でないならば分析モデルにかけられる状態にする関数
    """
    race_dt = dt.strptime(race_date, '%Y%m%d')
    # まずは新レースデータから騎手、馬idを抜き出しDBから各値をとってくる
    # そのレースのhorse_id, jockey_idがDB内にあるのはscrapeメソッドで担保済み
    horse_id_list = df['horse_id'].to_list()
    jockey_id_list = df['jockey_id'].to_list()
    with app.app_context():
      Session = sessionmaker(bind=db.engine)
      session = Session()
      horses = session.query(HorseModel).filter(HorseModel.horse_id.in_(horse_id_list)).all()
      jockeies = session.query(JockeyModel).filter(JockeyModel.jockey_id.in_(jockey_id_list)).all()

    # DBから取ってきた値の順番を取得データに合わせる
    horse_order_ave_dict = {}
    horse_order_ave_list = []
    for horse in horses:
      horse_order_ave_dict[horse.horse_id] = horse.order_ave_info
    # JSON形式のデータから、その日付に最も近い時点での馬の成績を抽出
    for horse_id in horse_id_list:
      for key_id, orders in horse_order_ave_dict.items():
        if horse_id == key_id:
          recent_date = max((key for key in orders if dt.strptime(key, '%Y-%m-%d') < race_dt), default=None)
          if bool(recent_date):
            horse_order_ave_list.append(orders[recent_date])
          else:
            horse_order_ave_list.append(None)
    df['馬直近成績'] = horse_order_ave_list

    jockey_top_ratio_dict = {}
    jockey_victory_ratio_dict = {}
    jockey_experience_dict = {}
    jockey_old_dict = {}
    jockey_top_ratio_list = []
    jockey_victory_ratio_list = []
    jockey_experience_list = []
    jockey_old_list = []
    for jockey in jockeies:
      jockey_top_ratio_dict[jockey.jockey_id] = jockey.top_ratio
      jockey_victory_ratio_dict[jockey.jockey_id] = jockey.victory_ratio
      jockey_experience_dict[jockey.jockey_id] = jockey.experience
      jockey_old_dict[jockey.jockey_id] = jockey.old

    for jockey_id in jockey_id_list:
      for key, value in jockey_top_ratio_dict.items():
        if jockey_id == key:
          jockey_top_ratio_list.append(value)
      for key, value in jockey_victory_ratio_dict.items():
        if jockey_id == key:
          jockey_victory_ratio_list.append(value)
      for key, value in jockey_experience_dict.items():
        if jockey_id == key:
          jockey_experience_list.append(value)
      for key, value in jockey_old_dict.items():
        if jockey_id == key:
          jockey_old_list.append(value)
    
    df['騎手直近単勝率'] = jockey_top_ratio_list
    df['騎手直近複勝率'] = jockey_victory_ratio_list
    df['騎手経験値'] = jockey_experience_list
    df['騎手年齢'] = jockey_old_list
    col = ['騎手直近単勝率', '騎手直近複勝率', '騎手経験値', '騎手年齢', '馬直近成績']
    
    return df[col]
