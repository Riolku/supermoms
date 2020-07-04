from flask import request, abort, Response, flash

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.auth.payment import create_payment, pop_payment, get_payment, complete_payment
from supermoms.database.products import Products, WorkshopUsers
from supermoms.database.cart_items import CartItems
from supermoms.database.utils import db_commit

@app.route("/products/")
def serve_shop():
  products = Products.query.filter_by(workshop = False, hidden = False).all()

  return render("shop.html", products = products, type = "Products")
  
@app.route("/workshops/")
def serve_workshops():
  workshops = Products.query.filter_by(workshop = True, hidden = False).all()
  
  return render("shop.html", products = workshops, type = "Workshops")
  
@app.route("/product/<int:id>", methods = ["GET", "POST"])
def serve_product(id):
  product = Products.query.filter_by(id = id).first_or_404()
  
  lang = get_lang()
  
  desc = product.cn_desc if lang == "CN" else product.en_desc
  
  name = product.cn_name if lang == "CN" else product.en_name
  
  ci = None if not user else CartItems.query.filter_by(uid = user.id, pid = id).first()
  
  if product.hidden and (not user or not user.admin): abort(404)
    
  if request.method == "POST":
    if not user:
      return redirect("/signin?next=%s" % request.path, code = 303)
    
    bad = False
    
    if product.workshop: qty = 1
    else:
      try:
        qty = int(request.form['qty'])
      except ValueError:
        flash("Please enter a valid integer for the quantity!", "error")
        
        bad = True
     
    if not bad:

      if product.workshop and ci:
        if 'remove_cart' in request.form:
          CartItems.remove(ci)

          flash("You have been unregistered.", "success")
        else:        
          flash("You cannot register again! Proceed to checkout to confirm your registration.", "error")

      elif product.workshop and (WorkshopUsers.query.filter_by(uid = user.id, pid = product.id).count() > 0):
        flash("You have already registered for this workshop!", "error")

      else:
        if ci:
          ci.count = min(qty, product.stock)

          if ci.count == 0: 
            CartItems.remove(ci)

          else:  
            db_commit()

        else:
          CartItems.add(uid = user.id, pid = id, count = qty)

        if product.workshop:
          flash("You have been registered! You must checkout to confirm your registration.", "success")

        else:
          flash("Items added to cart.", "success")
      
    # Get the cart item again cause it mightve been updated
    ci = CartItems.query.filter_by(uid = user.id, pid = id).first()
      
  registered = False
  cart = False
  
  if product.workshop:
    if ci: cart = True
      
    if user and WorkshopUsers.query.filter_by(uid = user.id, pid = product.id).count() > 0: registered = True
        
  cur_qty = 0
  
  if ci: cur_qty = ci.count
  
  return render("product.html", p = product, cur_qty = cur_qty, desc = desc, name = name, cart = cart, registered = registered)
  

@app.route("/product/<int:id>/image/")
def serve_product_image(id):
  product = Products.query.filter_by(id = id).first_or_404();
  
  if product.hidden and not user.admin: abort(404)

  return Response(product.image, mimetype = "image/png")
  

@app.route("/admin/products/", methods = ["GET", "POST"])
@admin_auth
def serve_admin_products():  
  if request.method == "POST":
    if 'delete' in request.form:
      id = int(request.form['delete'])
      
      Products.query.filter_by(id = id).delete()
      
      db_commit()
      
      flash("Product deleted!", "success")
      
    else:
      workshop = 'workshop' in request.form

      p = Products.add(en_name = "", cn_name = "", en_desc = "", cn_desc = "", stock = 0, image = b"", price = 0.0, workshop = workshop, hidden = True)

      return redirect("/admin/product/%d" % p.id, code = 303)
  
  products = Products.query.all()
  
  return render("admin/products.html", products = products)


@app.route("/admin/product/<int:id>", methods = ['GET', 'POST'])
@admin_auth
def serve_admin_product(id):  
  product = Products.query.filter_by(id = id).first_or_404();
  
  if request.method == "POST":    
    en_name = request.form['en_name']
    cn_name = request.form['cn_name']
    
    en_desc = request.form['en_desc']
    cn_desc = request.form['cn_desc']
    
    
    stock = request.form['stock']
    image = request.files['image'].read()
    price = request.form['price']
    hidden = 'publish' not in request.form
    
    bad = False
    
    try: 
      stock = int(stock)
    except ValueError:
      flash("Please enter a valid integer for the stock.", "success")
      
      bad = True
      
    try: 
      price = float(price)
    except ValueError:
      flash("Please enter a valid number for the price.", "success")
      
      bad = True

    if len(en_name) > 1023 or len(cn_name) > 1023:
      flash("Product name too long!", "error")

      bad = True
      
    if type(price) == float and price < 0.5 and price != 0:
      flash("Price must be either at least 50 cents or free!", "error")
      
      bad = True

    if len(en_desc) > 65535 or len(cn_desc) > 65535:
      flash("Product description too long!", "error")

      bad = True

    if len(image) > 2 ** 22:
      flash("Image too large! Maximum size is 4 MB!", "error")

      bad = True

    if not bad:
      product.stock = stock
      product.hidden = hidden
      
      if len(image) > 16: product.image = image
      
      product.en_name = en_name
      product.cn_name = cn_name
      
      product.en_desc = en_desc
      product.cn_desc = cn_desc
      
      product.price = price

      db_commit()

      flash("Product updated!", "success")
  
  return render("admin/edit_product.html", p = product)

@app.route("/view-cart/", methods = ["GET", "POST"])
@authorize
def serve_view_cart():
  citems = CartItems.query.filter_by(uid = user.id).all()
  
  pids = [ci.pid for ci in citems]
  
  ps = Products.query.filter(Products.id.in_(pids)).all()
  
  pmap = {p.id : p for p in ps}
  
  items = [(pmap[ci.pid], ci) for ci in citems]
  
  total = sum(it[0].price * it[1].count for it in items)
  
  if request.method == "POST":
    # Calculate total amount
    amt = total
    
    create_payment(amt, "/confirm/checkout/")
    
    if amt == 0: 
      complete_payment()
      
      return redirect("/confirm/checkout", code = 303)
    
    val = request.form['pay_method']
    
    if val == "paypal":
      return redirect('/pay/paypal', code = 303)
    
    return redirect('/pay/card', code = 303)
  
  return render("view_cart.html", items = items, total = total)

