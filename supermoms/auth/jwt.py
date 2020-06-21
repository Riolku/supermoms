import jwt

from supermoms import app

def make_jwt(payload):
  return jwt.encode(payload, app.secret_key).decode("utf-8")

def verify_jwt(token):
  return jwt.decode(token, app.secret_key)