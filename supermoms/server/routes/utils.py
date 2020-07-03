import misaka, urllib

from markupsafe import Markup

from supermoms import app
from flask import render_template

from supermoms.config import stripe_pkey
from supermoms.database.utils import db_commit

from supermoms.auth.manage_user import user, is_session_fresh, ensure_user
from supermoms.utils.time import get_time

from flask import request, redirect

# Globals in templates
@app.context_processor
def context_processor():
  return dict(
    user = user,
    get_time = get_time,
    locale = get_locale(),
    lang = get_lang(),
    path = request.path,
    query = request.args,
    stripe_pkey = stripe_pkey
  )

render = render_template

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
  
locale = {}

for lang in ["EN", "CN"]:
  with open("supermoms/assets/locale_%s.txt" % lang) as f:
    locale[lang] = {}
    for line in f.readlines():
      if line:
        a, b = line.split(maxsplit = 1)
        locale[lang][a] = b

def parse_accept_lang():
  h = request.headers.get('Accept-Language')
  
  if h is None: return "EN"
  
  h = h.lower()
  
  ls = h.split(",")
  
  best = [0, "EN"]
  
  for x in ls:
    x = x.strip()
    
    t = x.split(";")
    
    t[0] = t[0].strip()
    if len(t) > 1: t[1] = t[1].strip()
    
    if not t[0].startswith("en") and not t[0].startswith("zh"): continue
    
    if len(t) > 1 and t[1].startswith("q="):
      q = None
      
      try: q = float(t[1][2:])
      except ValueError: best = max(best, [1, t[0]])
      
      if q is not None:
        best = max(best, [q, t[0]])
    
    else:
      best = max(best, [1, t[0]])
      
  return "CN" if best[1].startswith("zh") else "EN"

def get_lang():
  l = request.cookies.get("lang")
    
  if l is None:
    if user: return user.lang
    
    return parse_accept_lang()
  
  return "CN" if l == "CN" else "EN"

@app.after_request
def set_user_lang(resp):
  if request.endpoint == "static":
    return resp
  
  if user:
    clang = get_lang()
    
    if user.lang == clang: return resp
    
    user.lang = clang
    
    db_commit()
    
  return resp

def get_locale():
  return locale[get_lang()]

@app.after_request
def add_content_lang(resp):
  resp.headers["Content-Language"] = ("zh-Hans" if get_lang() == "CN" else "en")
  
  return resp