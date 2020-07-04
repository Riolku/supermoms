import base64, json, re, time

from flask import redirect, request, flash, abort, jsonify, session

from datetime import datetime

from jwt.exceptions import ExpiredSignatureError

from supermoms.auth import login_user, logout_user, user, make_jwt, verify_jwt
from supermoms.database import BlogComments, BlogPosts, Products, Users, db_commit
from supermoms.mail import send_signin_email, send_signup_email
from .utils import *
from supermoms.utils.time import get_time

@app.route("/")
def serve_root():
  return render("index.html")

@app.route("/about/")
def serve_about():
  return render("about.html")

@app.route("/email-signin/", methods = ["GET", "POST"])
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
      # url_root allows the link to be accessed from anywhere
      # it should contain the protocol, host and starting `/` 
        
      send_signin_email(email, request.url_root + "signin-link/?token=%s" % make_jwt({ 
        "id": u.id,
        "email": email,
        "exp": int(time.time()) + 3600
      }))
      
    return redirect("/", code = 303)

@app.route("/signin-link/")
def serve_signin_link():
  try:
    data = verify_jwt(request.args.get("token", ""))
  except ExpiredSignatureError:
    flash(get_locale()["signin_link_exp"], "error")
    return redirect("/email-signin/", code = 303)
  
  if data is None:
    flash(get_locale()["signin_link_fail"], "error")
    return redirect("/email-signin/", code = 303)
  
  u = Users.query.filter_by(id = data["id"]).first()
  if u.email != data["email"]:
    flash(get_locale()["signin_link_email_changed"], "error")
    return redirect("/email-signin/", code = 303)
  
  if u is None:
    flash(get_locale()["signin_link_no_user"], "error")
    return redirect("/email-signin/", code = 303)
  
  login_user(u)
  flash(get_locale()["welcome_back"].replace("_", u.name), "success")
  return redirect("/edit-profile/", code = 303)
  
@app.route("/signin/", methods = ["GET", "POST"])
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

@app.route("/signup/", methods = ["GET", "POST"])
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
  
@app.route("/create-account/", methods = ["GET", "POST"])
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
    username = request.form["username"]
    password = request.form["password"]
    rpassword = request.form["rpassword"]

    fail = False

    if name.strip() == "" or username.strip() == "":
      fail = True
      flash(get_locale()["enter_nonempty_name"], "error")
    
    if Users.query.filter_by(username = username).count() > 0:
      fail = True
      flash(get_locale()["username_taken"], "error")

    if len(password) < 8:
      fail = True
      flash(get_locale()["password_too_short"], "error")
    elif password != rpassword:
      fail = True
      flash(get_locale()["password_mismatch"], "error")

    if fail:
      return render("signup.html", __field_name = name, __field_username = username, __field_email = email)

    login_user(Users.create(name, username, email, password, get_lang()))

    flash(get_locale()["welcome"].replace("_", name), "success")

    return redirect("/", code = 303)

@app.route("/signout/")
def serve_signout():
  if user:
    logout_user()
    
  flash(get_locale()["goodbye"], "success")
  
  return redirect(request.args.get("next", "/"), code = 303)

@app.route("/edit-profile/", methods = ["GET", "POST"])
@reauthorize
def serve_edit_profile():
  if request.method == "GET":
    return render("edit-profile.html", __field_name = user.name, __field_username = user.username, __field_email = user.email)
  else:
    name = request.form["name"]
    username = request.form["username"]
#    email = request.form["email"]
    password = request.form["password"]
    rpassword = request.form["rpassword"]
    
    fail = False
    
    if name.strip() == "" or username.strip() == "":
      fail = True
      flash(get_locale()["enter_nonempty_name"], "error")
      
    if username != user.username and Users.query.filter_by(username = username).count() > 0:
      fail = True
      flash(get_locale()["username_taken"], "error")
    
#     if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
#       fail = True
#       flash(get_locale()["invalid_email"], "error")
#     elif email != user.email and Users.query.filter_by(email = email).count() > 0:
#       fail = True
#       flash(get_locale()["email_taken"], "error")
    
    if password and len(password) < 8:
      fail = True
      flash(get_locale()["password_too_short"], "error")
    elif password and password != rpassword:
      fail = True
      flash(get_locale()["password_mismatch"], "error")
      
    if fail:
      return render("edit-profile.html", __field_name = name, __field_email = email)
    
#    if email != user.email:
#      pass # TODO: Send email-change email
    
    user.update(None, name, username, password if password else None)
    
    flash(get_locale()["updated_profile"], "success")
    
    return redirect("/edit-profile", code = 303)

@app.route("/signout-all/")
def serve_signout_all():
  if user:
    user.invalidate_tokens_before = int(time.time())
    db_commit()
  
  flash(get_locale()["goodbye"], "success")
  
  return redirect(request.args.get("next", "/"), code = 303)

@app.route("/blog")
@app.route("/blog/<int:page>")
def serve_blog(page = 1):
  return render("blog.html", posts = BlogPosts.query.filter_by(lang = get_lang()).all()[(page - 1) * 5:][:5])

@app.route("/post/<int:id>", methods = ["GET", "POST"])
def serve_post(id):
  if request.method == "GET":
    return render("post.html", post = BlogPosts.query.filter_by(id = id).first_or_404())
  else:
    comment = request.form["comment"]
    
    if comment.strip() == "":
      flash(get_locale()["comment_empty"], "error")
    else:
      BlogComments.add(content = comment, author = user.id, bid = id)
      db_commit()
    
    return redirect("/post/%d" % id, code = 303)

@app.route("/delete-comment/<int:id>", methods = ["POST"])
@authorize
def delete_comment(id):
  comment = BlogComments.query.filter_by(id = id).first()
  
  if comment is None:
    flash(get_locale()["comment_does_not_exist"], "error")
  elif not user.admin and comment.author != user.id:
    flash(get_locale()["comment_delete_no_permission"], "error")
  else:
    comment.deleted = True
    flash(get_locale()["comment_deleted"], "success")
    db_commit()
    
  return redirect("/post/%d" % comment.bid, code = 303)

@app.route("/delete-blog-post/<int:id>", methods = ["POST"])
@admin_auth
def delete_blog_post(id):
  post = BlogPosts.query.filter_by(id = id).first()
  
  if post is None:
    flash(get_locale()["post_does_not_exist"], "error")
  else:
    BlogPosts.query.filter_by(id = id).delete()
    flash(get_locale()["post_deleted"], "success")
    db_commit()
  
  return redirect("/blog", code = 303)

@app.route("/create-blog-post")
@admin_auth
def create_blog_post():
  bp = BlogPosts.add(title = "", content = "", author = user.id, lang = get_lang())
  db_commit()
  return redirect("/edit-blog-post/%d" % bp.id)

@app.route("/edit-blog-post/<int:id>", methods = ["GET", "POST"])
@admin_auth
def edit_blog_post(id):
  bp = BlogPosts.query.filter_by(id = id).first_or_404()
  
  if request.method == "GET":
    return render("edit-blog-post.html", __field_title = bp.title, __field_content = bp.content, __field_lang = bp.lang)
  else:
    bp.title = request.form["title"]
    bp.content = request.form["content"]
    bp.lang = "CN" if "lang" in request.form else "EN"
    bp.hidden = False
    db_commit()
    flash(get_locale()["saved_blog_post"], "success")
    return redirect("/blog", code = 303)

@app.route("/tos/")
def serve_tos():
  return render("tos.html")

@app.route("/privacy/")
def serve_privacy():
  return render("privacy.html")

@app.route("/favicon.ico")
def serve_favicon():
  return redirect("/static/ico/favicon.ico", code = 303)