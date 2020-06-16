from pharmacy import app

from pharmacy.database.users import Users
from pharmacy.utils.time import get_time

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
  
  user = session.get("user")

  if user is None: return

  uid = user.get("id")

  if uid is None: return

  u = Users.query.filter_by(id = int(uid)).first()

  if u is None: return

  if u:
    if user['time'] + 60 * 60 * 24 > get_time():
      user_manager.user = u


def login_user(u):
  user_manager.user = u
  
  session['user'] = dict(id = u.id, time = get_time())
  
def logout_user():
  user_manager.user = None
  
  del session['user']
