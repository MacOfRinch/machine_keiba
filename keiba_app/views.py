# coding: UTF-8
from keiba_app import app
from flask import render_template
from flask import request

@app.route('/')
def index():
  return render_template('keiba_app/index.html')

@app.route('/sampleform', methods=['GET', 'POST'])
def sample_form():
  if request.method == 'GET':
    return render_template('keiba_app/sampleform')
  elif request.method == 'POST':
    pass

