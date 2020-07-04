from supermoms import db

from .aliases import *
from .helper import Helper
from .users import Users
from .products import Products

class CartItems(Helper, dbmodel):
  __tablename__ = "cart_items"
  
  uid = dbcol(dbint, dbforkey(Users.id, ondelete = "CASCADE"), primary_key = True)
  pid = dbcol(dbint, dbforkey(Products.id), primary_key = True)
  count = dbcol(dbint, nullable = False)