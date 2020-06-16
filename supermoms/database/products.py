from pharmacy import db

from .aliases import *
from .helper import Helper

class Products(Helper, dbmodel):
  __tablename__ = "products"
  
  id = dbcol(dbint, primary_key = True)
  name = dbcol(dbstr(64), nullable = False) # The name displayed to the user
  desc = dbcol(dbstr(1024), nullable = False) # Product description
  stock = dbcol(dbint, nullable = False) # Count in stock
  

class ProductImages(Helper, dbmodel):
  __tablename__ = "product_images"
  
  id = dbcol(dbint, primary_key = True)
  pid = dbcol(dbint, dbforkey(Products.id), nullable = False)
  first = dbcol(dbbool, nullable = False, default = 0)