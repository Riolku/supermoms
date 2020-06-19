import urllib
from markupsafe import Markup

from supermoms import app

from supermoms.auth.manage_user import user, is_session_fresh
from supermoms.utils.time import get_time

from flask import request

# Globals in templates
@app.context_processor
def context_processor():
  return dict(
    user = user,
    get_time = get_time
  )

@app.template_filter("urlencode")
def urlencode_filter(s):
  if type(s) == "Markup":
    s = s.unescape()
  s = s.encode("utf-8")
  s = urllib.parse.quote_plus(s)
  return Markup(s)

#@app.before_request
def debug():
  print(request.environ)
  
  print()
  
  print(request.headers)
  
@app.route("/test")
def test_index():
  return str(is_session_fresh())