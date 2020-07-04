from flask import request, abort, flash

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.database.forums import SubForums, ForumThreads, ForumPosts
from supermoms.database.utils import db_commit

@app.route('/forum/')
def serve_forum():
  sub_fs = SubForums.query.filter_by(lang = get_lang()).all()
  
  return render("forum/forum.html", sub_fs = sub_fs)

@app.route('/forum/<int:id>', methods = ["GET", "POST"])
def serve_subforum(id):
  sub_f = SubForums.query.filter_by(id = id).first_or_404()
  
  if request.method == "POST":
    if not user: return redirect("/signin/?next=%s" % request.path, code = 303)
    
    if 'delete' in request.form:
      if not user.admin:
        flash("You do not have permission to delete threads!", "error")
        
      else:
        tid = request.form['delete']
      
        thread = ForumThreads.query.filter_by(id = tid).delete()
        
        db_commit()
        
        flash("Thread deleted!", "success")
      
    else:
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

        return redirect('/forum/%d/thread/%d' % (ft.id, fp.id))

  threads = ForumThreads.query.filter_by(sfid = id).all()
  
  return render("forum/sub_forum.html", sub_f = sub_f, threads = threads)

THREAD_POSTS_PER_PAGE = 25

@app.route('/forum/<int:sfid>/thread/<int:tid>', methods = ["GET", "POST"])
@app.route("/forum/<int:sfid>/thread/<int:tid>/<int:page>", methods = ["GET", "POST"])
def serve_thread(sfid, tid, page = 1):
  sub_f = SubForums.query.filter_by(id = sfid).first_or_404()
  
  thread = ForumThreads.query.filter_by(id = tid).first_or_404()
  
  if thread.sfid != sub_f.id: abort(404)
  
  if request.method == "POST":
    if not user: return redirect("/signin/?next=%s" % request.path, code = 303)
    
    if 'delete' in request.form:
      id = request.form['delete']
      
      post = ForumPosts.query.filter_by(id = id).first()
      
      if post and (post.uid == user.id or user.admin):
        post.deleted = True
        
        db_commit()
        
        flash("Post deleted!", "success")
        
      else:
        flash("You do not have permission to delete this post!", "error");
      
    else:
      content = request.form['content']
    
      if len(content) > 65535:
        flash("The content you entered is too long for a single post!", "error")
      
      else:
        ForumPosts.add(content = content, tid = tid, uid = user.id)
        
        flash("Your post was added!", "success")
  
  posts = ForumPosts.query.filter_by(tid = tid).order_by(ForumPosts.time).all()
  
  filtered_posts = posts[(page - 1) * THREAD_POSTS_PER_PAGE : page * THREAD_POSTS_PER_PAGE]
  
  uids = [fp.uid for fp in filtered_posts]
  
  users = Users.query.filter(Users.id.in_(uids)).all()
  
  u_dict = {u.id : u for u in users}
      
  user_list = [u_dict[fp.uid] for fp in filtered_posts]
  
  return render("forum/thread.html", sub_f = sub_f, thread = thread, content = zip(user_list, filtered_posts))
  

@app.route('/admin/forum/', methods = ["GET", "POST"])
@admin_auth
def serve_admin_forums():  
  if request.method == "POST":
    if 'delete' in request.form:
      id = int(request.form['delete'])
            
      SubForums.query.filter_by(id = id).delete()
      
      db_commit()
            
      flash("Sub forum deleted sucessfully.", "success")
      
    else:
      title = request.form['title']
      lang = "CN" if 'lang_cn' in request.form else "EN"
    
      if len(title) > 255:
        flash("The title you have entered is too long!", "error")

      else:
        flash("Sub forum added!", "success")
      
        SubForums.add(title = title, lang = lang)

  sub_fs = SubForums.query.all()
        
  return render("admin/forum.html", sub_fs = sub_fs)