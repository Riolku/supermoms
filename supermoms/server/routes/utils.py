import misaka, urllib

from markupsafe import Markup

from supermoms import app

from supermoms.auth.manage_user import user, is_session_fresh
from supermoms.utils.time import get_time

from flask import request, redirect

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

app.template_filter("markdown")(misaka.html)

def authorize(view):
  def _inner(*a, **k):
    if not user:
      return redirect("/signin?next=%s" % request.path)
    return view(*a, **k)
  _inner.__name__ = view.__name__
  return _inner

def reauthorize(view):
  def _inner(*a, **k):
    if not is_session_fresh():
      return redirect("/signin?next=%s&redir=no" % request.path)
    return view(*a, **k)
  _ret = authorize(_inner)
  _ret.__name__ = view.__name__
  return _ret

#@app.before_request
def debug():
  print(request.environ)
  
  print()
  
  print(request.headers)