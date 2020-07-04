import stripe

from flask import request, abort, Response, session, flash

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.auth.paypal import create_order, confirm_order
from supermoms.auth.payment import create_payment, pop_payment, get_payment, add_payment_method, complete_payment, refund_payment
from supermoms.database.products import Products
from supermoms.database.cart_items import CartItems
from supermoms.database.utils import db_commit

@app.route("/pay/card/", methods = ["GET", "POST"])
@authorize
def serve_pay_card():
  pay_obj = get_payment()
  
  if not pay_obj:
    return render("error_template.html", head = "Bad Request", message = "No payment data was configured when accessing the card payment portal."), 400

  if request.method == "POST":
    intent = stripe.PaymentIntent.retrieve(pay_obj['pay_id'])
    
    assert intent.status == "succeeded"
    
    complete_payment()
    
    return redirect(pay_obj['return_url'], code = 303)
      
  intent = stripe.PaymentIntent.create(
    amount = int(pay_obj['amount'] * 100),
    currency = 'cad'
  )
  
  add_payment_method('card', intent.id)
      
  return render("pay_card.html", amount = pay_obj['amount'], client_secret = intent.client_secret)
  

@app.route("/pay/paypal/")
@authorize
def serve_pay_paypal():
  pay_obj = get_payment()
  
  if not pay_obj:
    return render("error_template.html", head = "Bad Request", message = "No payment data was configured when accessing the paypal payment portal."), 400
  
  url, id = create_order(pay_obj['amount'])
    
  return redirect(url)
  

@app.route("/pay/paypal/cancel/")
def serve_pay_paypal_cancel():
  flash("Your order was cancelled." if en() else "您的订单被取消了。", "success")
  
  return redirect(request.args.get("next", "/"))
  

@app.route("/pay/paypal/confirm/")
@authorize
def serve_paypal_confirm():
  pay_obj = get_payment()
  
  complete_payment()
  
  refund_id = confirm_order(request.args['token'])
  
  add_payment_method('paypal', refund_id)
  
  return redirect(pay_obj['return_url'])