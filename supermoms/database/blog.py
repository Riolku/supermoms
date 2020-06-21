from supermoms import db

from .aliases import *
from .helper import Helper
from .users import Users
from .utils import db_commit

class BlogPosts(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  title = dbcol(dbstr(256), unique = False, nullable = False)
  content = dbcol(dbstr(65536), unique = False, nullable = False)
  author = dbcol(dbint, dbforkey(Users.id), nullable = False)
  
  __tablename__ = "blog_posts"
  
class BlogComments(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  pid = dbcol(dbint, dbforkey(BlogPosts.id), nullable = False)
  content = dbcol(dbstr(1024), unique = False, nullable = False)
  author = dbcol(dbint, dbforkey(Users.id), nullable = False)
  
  __tablename__ = "blog_comments"