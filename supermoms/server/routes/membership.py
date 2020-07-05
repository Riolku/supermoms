from flask import request, abort, Response, flash

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.auth.payment import create_payment, pop_payment, get_payment
from supermoms.database.products import Products
from supermoms.database.cart_items import CartItems
from supermoms.database.utils import db_commit
from supermoms.utils.time import get_time, DAY

@app.route('/membership/', methods = ['GET', "POST"])
def serve_membership():
  # Couple cases for display here
  
  # If they arent logged in, give them a link to /signin/?next=/membership
  
  # If they are and they haven't ever had a membership (user.premium_end == 0), 
    # "Buy your membership today"
    
  # If they have had a membership, either:
    # "Renew your membership, it has x days left" (or "less than one day")
    # "Renew your expired membership."
    
    
  if request.method == "POST":
    if not user: return redirect('/signin/?next=/membership')
    
    if user.premium_end - get_time() > 31 * DAY:
      flash("Your membership is not yet due for renewal!" if en() else "您的会员资格不需要续订呢", "error")
      
    else:
      create_payment(99, "/membership/confirm/")
      
      val = request.form['pay_method']
    
      if val == "paypal":
        return redirect('/pay/paypal', code = 303)

      return redirect('/pay/card', code = 303)
    
  return render("membership.html")
  
@app.route('/membership/confirm/')
@authorize
def confirm_membership():
  p = pop_payment()
  
  assert p['amount'] == 99
  assert p['return_url'] == '/membership/confirm/'
  
  user.extend_premium(366 * DAY)
  
  flash("You successfully purchased a membership!" if en() else "您成功购买了会员！", "success")
  
  return redirect("/")