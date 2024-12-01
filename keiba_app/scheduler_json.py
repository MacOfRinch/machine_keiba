import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from flask_apscheduler import APScheduler
import os
import json
import importlib

scheduler = APScheduler()
SCHEDULE_FILE = 'schedule.json'

# arg = scheduler 明示的にschedulerを渡す
def save_jobs_to_file(arg):
  jobs = []
  for job in arg.get_jobs():
    trigger = job.trigger.__class__.__name__
    trigger_name = trigger.split('Trigger')[0].lower()
    str_trigger = str(job.trigger)
    match = re.search(r'\[(.*)\]', str_trigger)
    jobs.append({
      'id': job.id,
      'func': f'{job.func_ref}',
      'trigger': trigger_name,
      'args': job.args,
      'kwargs': job.kwargs,
      'trigger_args': match.group(1) if match else str_trigger
    })
  with open(SCHEDULE_FILE, 'w') as f:
    json.dump(jobs, f, default=str, indent=4, ensure_ascii=False)

def load_jobs_from_file():
  print(' * Loading schedule file ...')
  if not os.path.exists(SCHEDULE_FILE):
    print(' * Schedule file not found.')
    return
  
  with open(SCHEDULE_FILE, 'r') as f:
    jobs_data = json.load(f)
  if not bool(jobs_data):
    print(' * Schedule file is empty. Check if it was actually saved.')
    return
  
  for job in jobs_data:
    if isinstance(job.get("trigger_args"), str):
      trigger_args = {}
      for item in job["trigger_args"].split(", "):
        key, value = item.split("=")
        key = key.strip('')
        value = value.strip('').strip("'")
        trigger_args[key] = value
      job["trigger_args"] = trigger_args

    scheduler.add_job(
      id=job['id'],
      func=resolve_func(job['func']),
      trigger=job['trigger'],
      args=job.get('args', []),
      kwargs=job.get('kwargs', {}),
      **job['trigger_args']
    )
  print(' * Schedule file was successfully loaded.')
  if not scheduler.running:
    scheduler.start()

def resolve_func(func_path):
  module_name, func_name = func_path.split(':')
  module = importlib.import_module(module_name)
  func = getattr(module, func_name)
  return func
