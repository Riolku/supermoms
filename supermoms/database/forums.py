from supermoms import db

from .aliases import *
from .helper import Helper
from .users import Users
from supermoms.utils.time import get_time

class SubForums(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  title = dbcol(dbstr(256), nullable = False)
  
  lang = dbcol(dbstr(16), nullable = False)
  
  __tablename__ = "sub_forums"
  

class ForumThreads(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  title = dbcol(dbstr(256), nullable = False)
  sfid = dbcol(dbint, dbforkey(SubForums.id, ondelete = "CASCADE"), nullable = False)
  
  __tablename__ = "forum_threads"
  

class ForumPosts(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  tid = dbcol(dbint, dbforkey(ForumThreads.id, ondelete = "CASCADE"), nullable = False)
  uid = dbcol(dbint, dbforkey(Users.id), nullable = False)
  
  content = dbcol(dbstr(65536), nullable = False)
  
  time = dbcol(dbint, default = get_time, nullable = False)
  
