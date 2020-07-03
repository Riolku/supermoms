import flask

def create_payment(amt, return_url):
  flask.session['pay'] = dict(amount = amt, return_url = return_url)
  
def get_payment():
  return flask.session.get('pay')
  
def pop_payment():
  if "pay" not in flask.session:
    return
  
  return flask.session.pop("pay")

