import base64, json, re, time

from flask import redirect, render_template, request, flash, abort, jsonify, session

from datetime import datetime

from jwt.exceptions import ExpiredSignatureError

from supermoms.auth import login_user, logout_user, user, make_jwt, verify_jwt
from supermoms.database import Users, Products, db_commit
from supermoms.mail import send_signin_email, send_signup_email
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

@app.route("/email-signin", methods = ["GET", "POST"])
def serve_email_signin():
  if request.method == "GET":
    return render("email-signin.html")
  else:
    email = request.form["email"]
    
    fail = False
    
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
      fail = True
      flash(get_locale()["invalid_email"], "error")
    
    if fail:
      return render("email-signin.html", __field_email = email)
    
    flash(get_locale()["sent_email_if_exist"], "success")
    
    u = Users.query.filter_by(email = email).first()
    
    if u:
      send_signin_email(email, request.url_root + "signin-link?token=%s" % make_jwt({
        "id": u.id,
        "email": email,
        "exp": int(time.time()) + 3600
      }))
      
    return redirect("/", code = 303)

@app.route("/signin-link")
def serve_signin_link():
  try:
    data = verify_jwt(request.args.get("token", ""))
  except ExpiredSignatureError:
    flash(get_locale()["signin_link_exp"], "error")
    return redirect("/email-signin", code = 303)
  if data is None:
    flash(get_locale()["signin_link_fail"], "error")
    return redirect("/email-signin", code = 303)
  u = Users.query.filter_by(id = data["id"]).first()
  if u.email != data["email"]:
    flash(get_locale()["signin_link_email_changed"], "error")
    return redirect("/email-signin", code = 303)
  if u is None:
    flash(get_locale()["signin_link_no_user"], "error")
    return redirect("/email-signin", code = 303)
  login_user(u)
  flash(get_locale()["welcome_back"].replace("_", u.name), "success")
  return redirect("/edit-profile", code = 303)
  
@app.route("/signin", methods = ["GET", "POST"])
def serve_signin():
  if user and request.args.get("redir") != "no":
    return redirect(request.args.get("next", "/"), code = 303)
  
  if request.method == "GET":
    return render("signin.html")
  else:
    email = request.form["email"]
    password = request.form["password"]
    
    u = Users.query.filter_by(email = email).first()
    
    if u and u.check_pass(password):
      login_user(u)
      
      if request.args.get("redir") != "no":
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
    email = request.form["email"]
    
    fail = False
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
      fail = True
      flash(get_locale()["invalid_email"], "error")
    elif Users.query.filter_by(email = email).count() > 0:
      fail = True
      flash(get_locale()["email_taken"], "error")
    
    flash(get_locale()["signup_email_sent"], "success")
    
    send_signup_email(email, request.url_root + "create-account?token=%s" % make_jwt({
      "email": email,
      "exp": int(time.time()) + 3600
    }))
    
    return redirect("/", code = 303)
  
@app.route("/create-account", methods = ["GET", "POST"])
def serve_create_account():
  try:
    data = verify_jwt(request.args.get("token", ""))
  except ExpiredSignatureError:
    flash(get_locale()["signup_link_exp"], "error")
    return redirect("/signup", code = 303)
  email = data["email"]
  
  if request.method == "GET":
    return render("create-account.html", __field_email = email)
  else:
    name = request.form["name"]
    password = request.form["password"]
    rpassword = request.form["rpassword"]
    card = request.form["card"]
    cvv = request.form["cvv"]
    postal = re.sub(r"\s", "", request.form["postal"])

    fail = False

    if name.strip() == "":
      fail = True
      flash(get_locale()["enter_nonempty_name"], "error")

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

    send_signup_email(email, request.url_root + "create-account?token=%s" % make_jwt({

    }))

    return redirect("/", code = 303)

@app.route("/signout")
def serve_signout():
  if user:
    logout_user()
    
  flash(get_locale()["goodbye"], "success")
  
  return redirect(request.args.get("next", "/"), code = 303)

@app.route("/edit-profile", methods = ["GET", "POST"])
@reauthorize
def serve_edit_profile():
  if not user:
    return redirect("/signin?next=/edit-profile")
  
  if request.method == "GET":
    return render("edit-profile.html", __field_name = user.name, __field_email = user.email, __field_card = user.card_num, __field_cvv = user.cvv, __field_postal = user.postal)
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
    elif email != user.email and Users.query.filter_by(email = email).count() > 0:
      fail = True
      flash(get_locale()["email_taken"], "error")
    
    if password and len(password) < 8:
      fail = True
      flash(get_locale()["password_too_short"], "error")
    elif password and password != rpassword:
      fail = True
      flash(get_locale()["password_mismatch"], "error")
      
    if postal and not re.match("([A-Za-z][0-9]){3}", postal):
      fail = True
      flash(get_locale()["invalid_postal"], "error")
      
    if fail:
      return render("edit-profile.html", __field_name = name, __field_email = email, __field_card = card, __field_cvv = cvv, __field_postal = postal)
    
    if email != user.email:
      pass # TODO: Send email-change email
    
    Users.query.filter_by(email = user.email).first().update(None, name, password if password else None, card, cvv, postal)
    
    flash(get_locale()["updated_profile"], "success")
    
    return redirect("/edit-profile", code = 303)

@app.route("/signout-all")
def serve_signout_all():
  if user:
    user.invalidate_tokens_before = int(time.time())
    db_commit()
  
  flash(get_locale()["goodbye"], "success")
  
  return redirect(request.args.get("next", "/"), code = 303)

@app.route("/blog")
def serve_blog():
  return render("blog.html")

@app.route("/tos")
def serve_tos():
  return render("tos.html")

@app.route("/privacy")
def serve_privacy():
  return render("privacy.html")

@app.errorhandler(404)
def serve_404(e):
  return "404"

@app.errorhandler(403)
def serve_403(e):
  return "403"

@app.route("/favicon.ico")
def serve_favicon():
  return redirect("/static/ico/favicon.ico", code = 303)