from supermoms import db

from .aliases import *
from .helper import Helper

class Products(Helper, dbmodel):
  __tablename__ = "products"
  
  id = dbcol(dbint, primary_key = True)
  name = dbcol(dbstr(1024), nullable = False) # The name displayed to the user
  desc = dbcol(dbstr(65536), nullable = False) # Product description
  stock = dbcol(dbint, nullable = False) # Count in stock
  image = dbcol(dbbinary, nullable = False)
  hidden = dbcol(dbbool, nullable = False, default = True)
  workshop = dbcol(dbbool, nullable = False)
  
  lang = dbcol(dbstr(16), nullable = False)
  
  @property
  def type(self):
    return "Workshop" if self.workshop else "Product"