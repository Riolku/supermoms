import stripe

from flask import request, abort, Response

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.auth.paypal import create_order, confirm_order
from supermoms.auth.payment import create_payment, pop_payment, get_payment
from supermoms.database.products import Products
from supermoms.database.cart_items import CartItems
from supermoms.database.utils import db_commit

@app.route("/pay/card/", methods = ["GET", "POST"])
@authorize
def serve_pay_card():
  if request.method == "POST":
    secret = request.form['client_secret']
    
    intent = stripe.PaymentIntent.retrieve(client_secret = client_secret)
  
    assert intent.state == "succeeded"
  
    return get_payment()['return_url']

  pay_obj = get_payment()
  
  if not pay_obj:
    return render("error_template.html", head = "Bad Request", message = "No payment data was configured when accessing the card payment portal."), 400
  
  intent = stripe.PaymentIntent.create(
    amount = int(pay_obj['amount'] * 100),
    currency = 'cad'
  )
  
  return render("pay_card.html", amount = pay_obj['amount'], client_secret = intent.client_secret)
  

@app.route("/pay/paypal/")
@authorize
def serve_pay_paypal():
  pay_obj = get_payment()
  
  if not pay_obj:
    return render("error_template.html", head = "Bad Request", message = "No payment data was configured when accessing the paypal payment portal."), 400
  
  return redirect(create_order(pay_obj['amount']))
  

@app.route("/pay/paypal/cancel/")
def serve_pay_paypal_cancel():
  flash("Your order was cancelled.", "success")
  
  return redirect(request.args.get("next", "/"))
  

@app.route("/pay/paypal/confirm/")
@authorize
def serve_paypal_confirm():
  pay_obj = get_payment()
  
  confirm_order(request.args['token'])
  
  return redirect(pay_obj['return_url'])

