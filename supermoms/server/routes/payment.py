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

@app.route("/shop")
def serve_shop():
  products = Products.query.filter_by(workshop = False).all()

  return render("shop.html", products = products)
  
@app.route("/workshops")
def serve_workshops():
  workshops = Products.query.filter_by(workshop = True).all()
  
  return render("shop.html", products = workshops)
  
@app.route("/product/<int:id>", methods = ["GET", "POST"])
def serve_product(id):
  product = Products.query.filter_by(id = id).first_or_404()
  
  if product.hidden and not user.admin: abort(404)
    
  if request.method == "POST":
    if not user:
      return redirect("/signin?next=%s" % request.path, code = 303)
      
    qty = int(request.form['qty'])
    
    ci = CartItems.query.filter_by(uid = user.id, pid = id).first()
    
    if ci:
      if qty == 0:
        del ci
      
      else:
        ci.count = qty
        db_commit()
      
    else:
      CartItems.add(uid = user.id, pid = id, count = qty)
      
  cur_ci = CartItems.query.filter_by(uid = user.id, pid = id).first()
  
  cur_qty = 0
  
  if cur_ci: cur_qty = cur_ci.count
  
  return render("product.html", product = product, cqty = cur_qty)
  

@app.route("/product/<int:id>/image/")
def serve_product_image(id):
  product = Products.query.filter_by(id = id).first_or_404();
  
  if product.hidden and not user.admin: abort(404)

  return Response(product.image, mimetype = "image/png")
  

@app.route("/admin/products/", methods = ["GET", "POST"])
@authorize
def serve_admin_products():
  if not user.admin: abort(403)
  
  if request.method == "POST":
    p = Products.add(name = "", desc = "", stock = 0, image = b"", hidden = True)
    
    return redirect("/admin/product/%d" % p.id, code = 303)
  
  products = Products.query.all()
  
  return render("admin/products.html", products = products)


@app.route("/admin/product/<int:id>")
@authorize
def serve_admin_product(id):
  if not user.admin: abort(403)
  
  product = Products.query.filter_by(id = id).first_or_404();
  
  return render("admin/edit_product.html", product = product)

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

@app.route("/pay/card/", methods = ["GET", "POST"])
@authorize
def serve_pay_card():
  if request.method == "POST":
    return pop_payment()['return_url']

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
  pay_obj = pop_payment()
  
  confirm_order(request.args['token'])
  
  return redirect(pay_obj['return_url'])

