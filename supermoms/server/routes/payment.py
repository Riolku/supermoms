import stripe

from flask import request

from .utils import *
from supermoms import app
from supermoms.auth.paypal import create_order, confirm_order
from supermoms.auth.payment import create_payment, pop_payment, get_payment

@app.route("/view-cart/", methods = ["GET", "POST"])
@authorize
def serve_view_cart():
  if request.method == "POST":
    # Calculate total amount
    amt = 10.99
    
    create_payment(amt, "/confirm/checkout/")
    
    val = request.form['pay_method']
    
    if val == "paypal":
      return redirect('/pay/paypal', code = 303)
    
    return redirect('/pay/card', code = 303)
  
  return render("view_cart.html")

@app.route("/pay/card/")
@authorize
def serve_pay_card():
  pay_obj = get_payment()
  
  if not pay_obj:
    return render("error_template.html", code = 400, message = "No payment data was configured when accessing the card payment portal."), 400
  
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
    return render("error_template.html", code = 400, message = "No payment data was configured when accessing the paypal payment portal."), 400
  
  return redirect(create_order(pay_obj['amount']))

@app.route("/pay/paypal/cancel/")
def serve_pay_paypal_cancel():
  return "Your order was cancelled."

@app.route("/pay/paypal/confirm/")
@authorize
def serve_paypal_confirm():
  pay_obj = pop_payment()
  
  confirm_order(request.args['token'])
  
  return redirect(pay_obj['return_url'])

