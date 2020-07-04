from supermoms import db

from .aliases import *
from .helper import Helper
from .users import Users

class Products(Helper, dbmodel):
  __tablename__ = "products"
  
  id = dbcol(dbint, primary_key = True)
  
  en_name = dbcol(dbstr(1024), nullable = False)
  cn_name = dbcol(dbstr(1024), nullable = False)
  
  en_desc = dbcol(dbstr(65536), nullable = False) # Product description
  cn_desc = dbcol(dbstr(65536), nullable = False) # Product description
  
  
  stock = dbcol(dbint, nullable = False) # Count in stock
  image = dbcol(dbbinary, nullable = False)
  hidden = dbcol(dbbool, nullable = False, default = True)
  workshop = dbcol(dbbool, nullable = False)
  price = dbcol(dbfloat, nullable = False)
  
  @property
  def type(self):
    return "Workshop" if self.workshop else "Product"
  
  
class WorkshopUsers(Helper, dbmodel):
  __tablename__ = "workshop_users"
  
  uid = dbcol(dbint, dbforkey(Users.id), primary_key = True)
  pid = dbcol(dbint, dbforkey(Products.id, ondelete = "CASCADE"), primary_key = True)