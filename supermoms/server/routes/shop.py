from flask import request, abort, Response

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.auth.payment import create_payment, pop_payment, get_payment
from supermoms.database.products import Products
from supermoms.database.cart_items import CartItems
from supermoms.database.utils import db_commit

@app.route("/shop")
def serve_shop():
  products = Products.query.filter_by(workshop = False, lang = get_lang(), hidden = False).all()

  return render("shop.html", products = products)
  
@app.route("/workshops")
def serve_workshops():
  workshops = Products.query.filter_by(workshop = True, lang = get_lang(), hidden = False).all()
  
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
@admin_auth
def serve_admin_products():  
  if request.method == "POST":
    lang = request.form['lang']
    workshop = request.form['workshop'] == 'workshop'
    
    if lang not in ['EN', 'CN']:
      flash("Invalid language!", "error");
      
    else:
      p = Products.add(name = "", desc = "", stock = 0, image = b"", lang = lang, workshop = workshop, hidden = True)
    
      return redirect("/admin/product/%d" % p.id, code = 303)
  
  products = Products.query.all()
  
  return render("admin/products.html", products = products)


@app.route("/admin/product/<int:id>", methods = ['GET', 'POST'])
@admin_auth
def serve_admin_product(id):  
  product = Products.query.filter_by(id = id).first_or_404();
  
  if request.method == "POST":
    name = request.form['name']
    desc = request.form['desc']
    stock = request.form['stock']
    image = request.form['image']
    hidden = request.form['hidden'] == 'hidden'
    
    try: 
      if not stock: stockdt = 0
      else: stockdt = int(stock)
      
    except ValueError: flash("Stock is not an integer!", "error")
  
    else:
      # stock was an integer
      # Using this weird construct for the first time, actually kind of nice...
      
      bad = False
      
      if stockdt < 0 and product.stock < -stockdt:
        flash("Stock change would make stock negative!", "error")
        
        bad = True
        
      if len(name) > 1023:
        flash("Product name too long!", "error")
        
        bad = True
        
      if len(desc) > 65535:
        flash("Product description too long!", "error")
        
        bad = True
        
      if len(image) > 2 ** 22:
        flash("Image too large! Maximum size is 4 MB!", "error")
        
        bad = True
        
      if not bad:
        product.stock += stockdt
        product.hidden = hidden
        product.image = image
        product.name = name
        product.desc = desc
        
        db_commit()
        
        flash("Product updated!", "success")
  
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