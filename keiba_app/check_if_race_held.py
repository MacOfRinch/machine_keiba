# 毎日実行してレースがある日を調べ、有効期間切れのデータを削除
# logicsの中に移動した方がいいかも
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keiba_app import db
from datetime import date as d
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
from .models.race_calender import RaceCalenderModel

def add_new_data():
  day = d.today()
  while day <= d.today() + relativedelta(days=1):
    half_year_later = day + relativedelta(months=6)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    url = 'https://race.netkeiba.com/top/?kaisai_date=' + day.strftime('%Y%m%d')
    driver.get(url)
    time.sleep(1)
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    # この要素があればレースあり
    if soup.find_all('div', attrs={'class': 'RaceList_Box'}):
      # レースの概要を取得
      infomations = []
      link_list = soup.find('div', attrs={'class': 'RaceList_Box'}).find_all('a', attrs={'href': re.compile(r'^../race/(shutuba|result)\.html')})
      for link in link_list:
        title = link.select('span.ItemTitle')[0].text
        race_id = ''.join(re.findall(r'\d+', link['href']))
        infomations.append({'title': title, 'race_id': race_id})
      from main import app
      with app.app_context():
        race_date_datum = db.session.query(RaceCalenderModel).all()
        dates_list = [date.race_date for date in race_date_datum]
        for infomation in infomations:
          race_dates = RaceCalenderModel(
            race_date=day.strftime('%Y%m%d'),
            race_title=infomation['title'],
            race_id=infomation['race_id'],
            expires_at=half_year_later
          )
          if not race_dates.race_date in dates_list:
            db.session.add(race_dates)
        db.session.commit()
    day += relativedelta(days=1)
    time.sleep(5)

def delete_old_data():
  from main import app
  with app.app_context():
    race_date_datum = db.session.query(RaceCalenderModel).all()
    for date_data in race_date_datum:
      expires_date = date_data.expires_at
      if expires_date < d.today():
        db.session.delete(date_data)
    db.session.commit()

if __name__ == '__main__':
  add_new_data()
  delete_old_data()
