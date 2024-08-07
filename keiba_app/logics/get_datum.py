import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from keiba_app import app, db
from ..models.race_result import RaceResultModel
from ..models.horse import HorseModel
from ..models.jockey import JockeyModel

half_year_later = dt.today() + relativedelta(months=6)
this_year = int(dt.today().year)

class UpdateDatum:
  @staticmethod
  def get_race_data(race_id: str) -> dict:
    url = "https://db.netkeiba.com/race/" + race_id + "/"

    response = requests.get(url)
    response.encoding = "EUC-JP"

    df = pd.read_html(response.text)[0]
    # 半角スペースがあったら除去
    df = df.rename(columns=lambda x: x.replace(' ', ''))
    df['predict_flag'] = True

    soup = BeautifulSoup(response.text, "html.parser")
    main_text = soup.select("div.data_intro h1")[0].text
    if '新馬' in main_text:
      df['predict_flag'] = False
    elif '未出走' in main_text:
      df['predict_flag'] = False

    sub_text = soup.select('p.smalltxt')[0].text
    date_str = re.findall(r'\S+', sub_text)[0]
    date = dt.strptime(date_str, '%Y年%m月%d日')
    df['race_date'] = [date] * len(df)
    # 今度はお馬さんidと騎手さんid
    horse_id_list = []
    jockey_id_list = []

    horse_link_list = soup.find('table', attrs={'summary': 'レース結果'}).find_all('a', attrs={'href': re.compile(r'^/horse/')})
    for horse_link in horse_link_list:
      horse_id = ''.join(re.findall(r'\d+', horse_link['href']))
      horse_id_list.append(horse_id)

    jockey_link_list = soup.find('table', attrs={'summary': 'レース結果'}).find_all('a', attrs={'href': re.compile(r'^/jockey/result/recent/')})
    for jockey_link in jockey_link_list:
      jockey_id = ''.join(re.findall(r'\d+', jockey_link['href']))
      jockey_id_list.append(jockey_id)

    df['horse_id'] = horse_id_list
    df['jockey_id'] = jockey_id_list
    df.index = [race_id] * len(df)

    with app.app_context():
      for _, row in df.iterrows():
        race_data = RaceResultModel(
          race_id=race_id,
          order=row['着順'],
          horse_name=row['馬名'],
          horse_id=row['horse_id'],
          jockey_name=row['騎手'],
          jockey_id=row['jockey_id'],
          odds=row['単勝'],
          race_date=row['race_date'],
          expires_at=row['race_date']+relativedelta(months=6),
          predict_flag=row['predict_flag']
        )
        db.session.add(race_data)
      db.session.commit()
    return {'horse_id_list': horse_id_list, 'jockey_id_list': jockey_id_list}

  @staticmethod
  def get_horse_data(horse_id: str) -> None:
    url = 'https://db.netkeiba.com/horse/' + horse_id + '/'
    response = requests.get(url)
    response.encoding = 'EUC-JP'
    html = response.text
    
    df = pd.read_html(html)[3]
    if df.columns[0] == '受賞歴':
      df = pd.read_html(html)[4]
    df.index = [horse_id] * len(df)
    df['日付'] = df['日付'].apply(lambda x: dt.strptime(x, '%Y/%m/%d'))
    df = df.loc[df['日付'] >= (dt.today() + relativedelta(months=-6))]
    # df['着順'] = df['着順'].apply(lambda x: int(x))
    rows = []
    for _, row in df.iterrows():
      try:
        rows.append(int(row['着順']))
      except ValueError:
        continue
    try:
      order_ave = sum(rows) / len(rows)
    except ZeroDivisionError:
      order_ave = 0
    
    with app.app_context():
      horse_info = db.session.query(HorseModel).filter(HorseModel.horse_id == horse_id).first()
      if horse_info:
        horse_info.order_ave = order_ave
        horse_info.expires_at = half_year_later
      else:
        horse_data = HorseModel(
          horse_id=horse_id,
          order_ave=order_ave,
          expires_at=half_year_later
        )
        db.session.add(horse_data)
      db.session.commit()
    return

  @staticmethod
  def get_jockey_data(jockey_id: str) -> None:
    url = 'https://db.netkeiba.com/jockey/result/' + jockey_id + '/'
    response = requests.get(url)
    response.encoding = 'EUC-JP'
    html = response.text

    df = pd.read_html(html)[0]

    soup = BeautifulSoup(html, 'html.parser')
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
      jockey_info = db.session.query(JockeyModel).filter(JockeyModel.jockey_id == jockey_id).first()
      if jockey_info:
        jockey_info.old = old
        jockey_info.top_ratio = top_ratio
        jockey_info.victory_ratio = victory_ratio
        jockey_info.experience = experience
        jockey_info.expires_at = half_year_later
      else:
        jockey_data = JockeyModel(
          jockey_id=jockey_id,
          old=old,
          top_ratio=top_ratio,
          victory_ratio=victory_ratio,
          experience=experience,
          expires_at=half_year_later
        )
        db.session.add(jockey_data)
      db.session.commit()
    return
