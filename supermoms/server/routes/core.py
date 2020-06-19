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
  return render_template(*a, **k, locale = get_locale(), lang = lang, path = request.path, query = request.args)

def get_locale():
  return locale[request.cookies.get("lang", "EN")]

@app.route("/")
def serve_root():
  return render("index.html")

@app.route("/about")
def serve_about():
  return render("about.html")

@app.route("/signin", methods = ["GET", "POST"])
def serve_signin():
  if user:
    return redirect(request.args.get("next", "/"), code = 303)
  
  if request.method == "GET":
    return render("signin.html")
  else:
    email = request.form["email"]
    password = request.form["password"]
    
    u = Users.query.filter_by(email = email).first()
    
    if u and u.check_pass(password):
      login_user(u)
      
      flash(get_locale()["welcome_back"].replace("_", u.name), "success")
    
      return redirect(request.args.get("next", "/"), code = 303)
    
    flash("Invalid Credentials!", "error")
    
    return render("signin.html", __field_email = email)

@app.route("/signup", methods = ["GET", "POST"])
def serve_signup():
  if user:
    return redirect(request.args.get("next", "/"), code = 303)
  
  if request.method == "GET":
    return render("signup.html")
  else:
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    rpassword = request.form["rpassword"]
    card = request.form["card"]
    cvv = request.form["cvv"]
    postal = re.sub(r"\s", "", request.form["postal"])
    
    fail = False
    
    if name.strip() == "":
      fail = True
      flash(get_locale()["enter_nonempty_name"], "error")
    
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
      fail = True
      flash(get_locale()["invalid_email"], "error")
    elif Users.query.filter_by(email = email).count() > 0:
      fail = True
      flash(get_locale()["email_taken"], "error")
    
    if len(password) < 8:
      fail = True
      flash(get_locale()["password_too_short"], "error")
    elif password != rpassword:
      fail = True
      flash(get_locale()["password_mismatch"], "error")
      
    if postal and not re.match("([A-Za-z][0-9]){3}", postal):
      fail = True
      flash(get_locale()["invalid_postal"], "error")
      
    if fail:
      return render("signup.html", __field_name = name, __field_email = email)
    
    login_user(Users.create(name, email, password, card, cvv, postal))
    
    flash(get_locale()["welcome"].replace("_", name), "success")
    
    return redirect("/", code = 303)

@app.route("/signout")
def serve_signout():
  logout_user()
  
  flash(get_locale()["goodbye"], "success")
  
  return redirect(request.args.get("next", "/"), code = 303)

@app.route("/edit-profile", methods = ["GET", "POST"])
def serve_edit_profile():
  if not user:
    return redirect("/signin?next=/edit-profile")
  
  if request.method == "GET":
    return render("edit-profile.html")
  return ""

@app.errorhandler(404)
def serve_404(e):
  return "404"

@app.errorhandler(403)
def serve_403(e):
  return "403"

@app.route("/favicon.ico")
def serve_favicon():
  return redirect("/static/ico/favicon.ico", code = 303)