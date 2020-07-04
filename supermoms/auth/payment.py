import flask, stripe

from .paypal import refund_order

def create_payment(amt, return_url):
  flask.session['pay'] = dict(amount = amt, return_url = return_url)
  
def add_payment_method(method, pay_id):
  flask.session['pay']['method'] = method
  flask.session['pay']['pay_id'] = pay_id
  
  flask.session.modified = True
  
def complete_payment():
  flask.session['pay']['complete'] = True
  
  flask.session.modified = True
  
def refund_payment(pay_obj):
  method = pay_obj['method']
  id = pay_obj['pay_id']
  
  if method == "paypal":
    refund_order(id)
    
  else:
    stripe.Refund.create(
      payment_intent = id
    )
  
  
def get_payment():
  return flask.session.get('pay')
  
def pop_payment():
  if "pay" not in flask.session:
    return
  
  return flask.session.pop("pay")

