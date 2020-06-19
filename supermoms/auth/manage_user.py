from supermoms import app

from supermoms.database.users import Users
from supermoms.utils.time import get_time

from flask import request, session

from werkzeug.local import Local

# Setup a thread proxy object
user_manager = Local()
user = user_manager('user')

@app.before_request
def resolve_user():
  # If the request endpoint is static, don't resolve the user
  if request.endpoint == "static":
    return
  
  user_manager.user = None
  
  user_d = session.get("user")

  if user_d is None: return

  uid = user_d.get("id")

  if uid is None: return

  u = Users.query.filter_by(id = int(uid)).first()

  if u is None: return

  if u:
    if user_d['time'] + 7 * 60 * 60 * 24 > get_time():
      user_manager.user = u

def is_session_fresh():
  assert user is not None, "You must have an active user to call is_session_fresh"
  
  if session['user']['time'] + 60 * 60 > get_time():
    return True
  
  return False

def refresh_user(u):
  assert user is not None, "You must have an active user to call refresh_user"
  
  session['user']['time'] = get_time()

def login_user(u):
  user_manager.user = u
  
  session['user'] = dict(id = u.id, time = get_time())
  
def logout_user():
  user_manager.user = None
  
  del session['user']
