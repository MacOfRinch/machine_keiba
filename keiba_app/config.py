from dotenv import load_dotenv
import os

# タスクの多重登録を防ぐため一時的にDEBUG = Falseにしている
DEBUG = False
JSON_AS_ASCII = False
SCHEDULER_API_ENABLED = True
SCHEDULER_TIMEZONE = 'Asia/Tokyo'

# DB接続設定
load_dotenv()
SQLALCHEMY_DATABASE_URI= 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
      'user': os.getenv('DB_USER'),
      'password': os.getenv('DB_PASS'),
      'host': os.getenv('DB_HOST_DEV'),
      'db_name': os.getenv('DB_NAME')
  })
SQLALCHEMY_TRACK_MODIFICATIONS = True
