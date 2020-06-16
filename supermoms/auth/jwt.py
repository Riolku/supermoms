import jwt

from pharmacy import app

def make_jwt(payload):
  try:
    return jwt.encode(payload, app.secret_key).decode("utf-8")
  except:
    return

def verify_jwt(token):
  try:
    return jwt.decode(token, app.secret_key).encode("utf-8")
  except:
    return