from pharmacy import db

from .aliases import *
from .helper import Helper
from .users import Users
from .products import Products

class CartItems(Helper, dbmodel):
  uid = dbcol(dbint, dbforkey(Users.id), primary_key = True)
  pid = dbcol(dbint, dbforkey(Products.id), primary_key = True)
  count = dbcol(dbint, nullable = False)