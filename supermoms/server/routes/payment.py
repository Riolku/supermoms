import stripe

from .utils import *
from supermoms import app
from supermoms.auth.paypal import create_order

@app.route("/pay/card")
@authorize
def serve_pay_card():
  intent = stripe.PaymentIntent.create(
    amount= 1099,
    currency = 'cad'
  )
  
  return render("pay_card.html", client_secret = intent.client_secret)

@app.route("/pay/paypal")
@authorize
def serve_pay_paypal():
  return redirect(create_order(10.99))