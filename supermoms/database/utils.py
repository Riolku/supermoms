from pharmacy import db

def db_commit():
  db.session.commit()