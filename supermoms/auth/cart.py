import flask

from supermoms.database.cart_items import CartItems
from supermoms.database.products import Products, ProductOrders
from .manage_user import user
from supermoms.database.utils import db_commit

def store_cart():
  cis = CartItems.query.filter_by(uid = user.id).all()
  
  flask.session['cart'] = {}
  
  for x in cis:
    flask.session['cart'][x.pid] = x.count
    
  print(flask.session)
    
def check_cart_same():
  cis = CartItems.query.filter_by(uid = user.id).all()

  for x in cis:
    if flask.session['cart'][str(x.pid)] != x.count:
      return False
    
  return True

def validate_cart():
  cis = CartItems.query.filter_by(uid = user.id).all()
  
  pids = [ci.pid for ci in cis]
  
  ps = Products.query.filter(Products.id.in_(pids)).all()
  
  pmap = {p.id : p for p in ps}
  
  items = [(pmap[ci.pid], ci) for ci in cis]
  
  good = True
  
  for p, ci in items:
    if p.stock < ci.count:
      ci.count = min(ci.count, p.stock)
      
      if ci.count == 0:
        CartItems.remove(ci, _flush = False)
        
      good = False
      
  db_commit()

  return good

def process_cart():
  cart = flask.session.pop("cart")
  
  pids = list(cart.keys())
  
  ps = Products.query.filter(Products.id.in_(pids)).all()
  
  for p in ps:
    ProductOrders.add(uid = user.id, pid = p.id, count = cart[str(p.id)], _flush = False)
    
  CartItems.query.filter_by(uid = user.id).delete()
  
  db_commit()