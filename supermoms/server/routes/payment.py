import stripe

from .utils import *
from supermoms import app
from supermoms.auth.paypal import create_order, confirm_order

@app.route("/pay/card/")
@authorize
def serve_pay_card():
  intent = stripe.PaymentIntent.create(
    amount= 1099,
    currency = 'cad'
  )
  
  return render("pay_card.html", client_secret = intent.client_secret)

@app.route("/pay/paypal/")
@authorize
def serve_pay_paypal():
  return redirect(create_order(10.99))

@app.route("/pay/paypal/cancel")
def serve_pay_paypal():
  return "Your order was cancelled."

@app.route("/pay/paypal/confirm/")
@authorize
def serve_paypal_confirm():
  confirm_order(request.args['token'])
  
  return redirect("/checkout/confirm")

@app.route("/checkout/confirm/")
@authorize
def serve_paypal_confirm():
  return "Your payment was captured and your order was confirmed. Thank you!"