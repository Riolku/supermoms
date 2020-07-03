from supermoms import db

import time

def db_commit():
  db.session.commit()
  
def get_time():
  return int(time.time())