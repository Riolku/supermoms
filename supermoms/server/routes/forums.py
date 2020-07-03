from flask import request, abort

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.database.forums import SubForums, ForumThreads, ForumPosts

@app.route('/forum/')
def serve_forum():
  sub_fs = SubForums.query.filter_by(lang = get_lang()).all()
  
  return render("forum/forum.html", sub_fs = sub_fs)

@app.route('/forum/<int:id>')
def serve_subforum(id):
  sub_f = SubForums.query.filter_by(id = id).first_or_404()
  
  if request.method == "POST":
    if not user: return redirect("/signin/?next=/forum/%d" % id, code = 303)
    
    title = request.form['title']
    content = request.form['content']
    
    bad = False
    
    if len(title) > 255:
      flash("The title you have entered is too long!", "error") # replace with locale['title_too_long']
      bad = True  
    
    if len(content) > 65535:
      flash("The content you have entered is too long for a single post!", "error")
      bad = True
      
    if not bad:
      ft = ForumThreads.add(title = title, sfid = id)
      
      fp = ForumPosts.add(uid = user.id, tid = ft.id, content = content)
      
      return redirect('/forum/%d/thread/%d' % ft.id)
  
  threads = ForumThreads.query.filter_by(sfid = id).all()
  
  return render("forum/sub_forum.html", sub_f = sub_f, threads = threads)

THREAD_POSTS_PER_PAGE = 25

@app.route('/forum/<int:sfid>/thread/<int:tid>')
@app.route("/forum/<int:sfid>/thread/<int:tid>/<int:page>")
def serve_thread(sfid, tid, page = 1):
  sub_f = SubForums.query.filter_by(id = sfid).first_or_404()
  
  thread = ForumThreads.query.filter_by(id = tid).first_or_404()
  
  if thread.sfid != sub_f.id: abort(404)
  
  if request.method == "POST":
    if not user: return redirect("/signin/?next=/forum/%d/thread/%d/%d" % (sfid, tid, page), code = 303)
    
    content = request.form['content']
    
    if len(content) > 65535:
      flash("The content you entered is too long for a single post!", "error")
      
    else:
      ForumPosts.add(content = content, tid = tid, uid = user.id)
  
  posts = ForumPosts.query.filter_by(tid = tid).order_by(ForumPosts.time).all()
  
  filtered_posts = posts[(page - 1) * THREAD_POSTS_PER_PAGE : page * THREAD_POSTS_PER_PAGE]
  
  return render("forum/thread.html", sub_f = sub_f, thread = thread, posts = filtered_posts)
  

@app.route('/admin/forum/')
@admin_auth
def serve_admin_forums():  
  if request.method == "POST":
    if 'delete' in request.form:
      id = request.form['delete']
      
      sf = SubForums.query.filter_by(id = id).delete()
      
    else:
      title = request.form['title']
    
      if len(title) > 255:
        flash("The title you have entered is too long!", "error")

      else:
        SubForums.add(title = title)

  sub_fs = SubForums.query.filter_by(lang = get_lang()).all()
        
  return render("admin/forum.html", sub_fs = sub_fs)