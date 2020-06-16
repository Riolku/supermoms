from supermoms import db

def db_commit():
  db.session.commit()