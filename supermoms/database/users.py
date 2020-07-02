from supermoms import db

import argon2

from .aliases import *
from .helper import Helper
from .utils import db_commit

from supermoms.utils.time import get_time

from os import urandom

class Users(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  name = dbcol(dbstr(256), unique = False, nullable = False)
  email = dbcol(dbstr(256), unique = True, nullable = False)
  
  lang = dbcol(dbstr(16), unique = False, nullable = False)

  admin = dbcol(dbbool, nullable = False, default = False)
  
  premium_end = dbcol(dbint, nullable = False, default = 0)
  
  salt = dbcol(dbbinary, nullable = False)
  pass_hash = dbcol(dbbinary, nullable = False)
  
  invalidate_tokens_before = dbcol(dbint, nullable = False, default = 0)
  
  @property
  def premium(self):
    return self.premium_end > get_time()
  
  
  def extend_premium(self, duration):
    self.premium_end = max(self.premium_end, get_time()) + duration
  
  # Create a new user with the specified name, email, password and language
  def create(name, email, password, lang):
    s = urandom(16)
    
    ph = argon2.argon2_hash(password, s)
    
    return Users.add(name = name, email = email, salt = s, pass_hash = ph, lang = lang)
    
  # Hash the password with the user's salt
  def hash(self, pword):
    return argon2.argon2_hash(pword, self.salt)
    
  # Check that the password provided is the same as the stored one
  def check_pass(self, pword):
    return self.hash(pword) == self.pass_hash
  
  # Try to login a user and return them, otherwise Falsy
  def login(email, password):
    u = Users.query.filter_by(email = email).first()
    
    if u is None: return None
    
    if not u.check_pass(password):
      return False
    
    return u
  
  # Update a user object
  def update(self, email = None, name = None, password = None):
    if email is not None:
      self.email = email
      
    if name is not None:
      self.name = name
      
    if password is not None:
      self.pass_hash = self.hash(password)
    
    db_commit()
  
  __tablename__ = "users"