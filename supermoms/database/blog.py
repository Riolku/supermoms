from supermoms import db

from .aliases import *
from .helper import Helper
from .users import Users
from .utils import db_commit, get_time

class BlogPosts(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  create_time = dbcol(dbint, default = get_time, nullable = False)
  title = dbcol(dbstr(256), unique = False, nullable = False)
  content = dbcol(dbstr(65536), unique = False, nullable = False)
  author = dbcol(dbint, dbforkey(Users.id), nullable = False)
  lang = dbcol(dbstr(256), unique = False, nullable = False)
  hidden = dbcol(dbbool, default = True, unique = False, nullable = False)
  
  @property
  def comments(self):
    return BlogComments.query.filter_by(bid = self.id).order_by(BlogComments.create_time.asc()).all()
  
  __tablename__ = "blog_posts"
  
class BlogComments(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  create_time = dbcol(dbint, default = get_time, nullable = False)
  bid = dbcol(dbint, dbforkey(BlogPosts.id, ondelete = "CASCADE"), nullable = False)
  content = dbcol(dbstr(1024), unique = False, nullable = False)
  author = dbcol(dbint, dbforkey(Users.id), nullable = False)
  
  deleted = dbcol(dbbool, default = False, nullable = False)
  
  __tablename__ = "blog_comments"