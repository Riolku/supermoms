import json, re

from flask import redirect, render_template, request, flash, abort, jsonify, session

from datetime import datetime

from supermoms.auth import login_user, logout_user, user
from supermoms.database import Users, Products
from supermoms.server.routes.utils import *
from supermoms.utils.time import get_time

locale = {}

for lang in ["EN", "CN"]:
  with open("supermoms/assets/locale_%s.txt" % lang) as f:
    locale[lang] = {}
    for line in f.readlines():
      if line:
        a, b = line.split(maxsplit = 1)
        locale[lang][a] = b

def render(*a, **k):
  lang = request.cookies.get("lang", "EN")
  return render_template(*a, **k, locale = locale[lang], lang = lang)

@app.route("/")
def serve_root():
  return render("index.html")

@app.route("/about")
def serve_about():
  return render("about.html")

@app.route("/signup", methods = ["GET", "POST"])
def serve_signup():
  return render("signup.html")

@app.errorhandler(404)
def serve_404(e):
  return "404"

@app.errorhandler(403)
def serve_403(e):
  return "403"

@app.route("/favicon.ico")
def serve_favicon():
  return redirect("/static/ico/favicon.ico", code = 303)