from keiba_app import app

@app.route('/')
def index():
  return 'オラ競馬予想すっぞ！'
