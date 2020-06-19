from supermoms import db

import argon2

from .aliases import *
from .helper import Helper

from os import urandom

class Users(dbmodel, Helper):
  id = dbcol(dbint, primary_key = True)
  
  name = dbcol(dbstr(256), unique = False, nullable = False)
  email = dbcol(dbstr(256), unique = True, nullable = False)

  admin = dbcol(dbbool, nullable = False, default = False)
  
  card_num = dbcol(dbstr(64), nullable = False, default = "")
  cvv = dbcol(dbstr(16), nullable = False, default = "")
  postal = dbcol(dbstr(16), nullable = False, default = "")
  
  salt = dbcol(dbbinary, nullable = False)
  pass_hash = dbcol(dbbinary, nullable = False)
  
  # Create a new user with the specified name, email, password, credit card number, and CVV
  def create(name, email, password, card_num, cvv, postal):
    s = urandom(16)
    
    ph = argon2.argon2_hash(password, s)
    
    return Users.add(name = name, email = email, salt = s, pass_hash = ph, card_num = card_num, cvv = cvv, postal = postal)
    
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
  def update(self, email = None, name = None, password = None, card_num = None, cvv = None):
    if email is not None:
      self.email = email
      
    if name is not None:
      self.name = name
      
    if password is not None:
      self.pass_hash = self.hash(password)
      
    if card_num is not None:
      self.card_num = card_num
      
    if cvv is not None:
      self.cvv = cvv
  
  __tablename__ = "users"