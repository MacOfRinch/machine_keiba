from keiba_app import app, db
from ..models.horse import HorseModel
from ..models.jockey import JockeyModel

from sqlalchemy.orm import sessionmaker
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

class NewRace:
  @staticmethod
  def scrape(new_race_id) -> pd.DataFrame:
    url = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + new_race_id
    try:
      response = requests.get(url)
      response.encoding = 'EUC-JP'

      soup = BeautifulSoup(response.text, 'html.parser')
      main_text = soup.select('div.RaceList_Item02 h1')
      if '新馬' in main_text:
        return
      elif '未出走' in main_text:
        return
      
      df = pd.read_html(response.text)[0]
      df = df.rename(columns=lambda x: x.replace(' ', ''))

      horse_id_list = []
      jockey_id_list = []
      horse_link_list = soup.find('table', attrs={'class': 'Shutuba_Table'}).find_all('a', attrs={'href': re.compile(r'^https://db.netkeiba.com/horse/\d+')})
      for horse_link in horse_link_list:
        horse_id = ''.join(re.findall(r'\d+', horse_link['href']))
        horse_id_list.append(horse_id)
          
      jockey_link_list = soup.find('table', attrs={'class': 'Shutuba_Table'}).find_all('a', attrs={'href': re.compile(r'^https://db.netkeiba.com/jockey/result/recent/\d+')})
      for jockey_link in jockey_link_list:
        jockey_id = ''.join(re.findall(r'\d+', jockey_link['href']))
        jockey_id_list.append(jockey_id)
          
      df['horse_id'] = horse_id_list
      df['jockey_id'] = jockey_id_list
    except Exception as e:
      print(e)
      return
    return df
  
  @staticmethod
  def analyze(df: pd.DataFrame):
    """
    scrapeで集めたレースデータを分析モデルにかけられる状態にする関数
    """
    # まずは新レースデータから騎手、馬idを抜き出しDBから各値をとってくる
    horse_id_list = df['horse_id'].to_list()
    jockey_id_list = df['jockey_id'].to_list()
    with app.app_context():
      Session = sessionmaker(bind=db.engine)
      session = Session()
    # 書き方合ってるか要リファクタリング　ラムダ式とか使えないか？これ
      horses = session.query(HorseModel).filter(HorseModel.horse_id.in_(horse_id_list)).all()
      jockeies = session.query(JockeyModel).filter(JockeyModel.jockey_id.in_(jockey_id_list)).all()

    # DBから取ってきた値の順番をデータに合わせる
    horse_order_ave_dict = {}
    horse_order_ave_list = []
    for horse in horses:
      horse_order_ave_dict[horse.horse_id] = horse.order_ave
    
    for horse_id in horse_id_list:
      for key, value in horse_order_ave_dict:
        if horse_id == key:
          horse_order_ave_list.append(value)
    df['horse_order_ave'] = horse_order_ave_list

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
      for key, value in jockey_top_ratio_dict:
        if jockey_id == key:
          jockey_top_ratio_list.append(value)
      for key, value in jockey_victory_ratio_dict:
        if jockey_id == key:
          jockey_victory_ratio_list.append(value)
      for key, value in jockey_experience_dict:
        if jockey_id == key:
          jockey_experience_list.append(value)
      for key, value in jockey_old_dict:
        if jockey_id == key:
          jockey_old_list.append(value)
    
    df['horse_order_ave'] = horse_order_ave_list
    df['jockey_top'] = jockey_top_ratio_list
    df['jockey_victory'] = jockey_victory_ratio_list
    df['jockey_experience'] = jockey_experience_list
    df['jockey_old'] = jockey_old_list
    col = ['horse_order_ave', 'jockey_top', 'jockey_victory', 'jockey_experience', 'jockey_old']
    
    return df[col]
