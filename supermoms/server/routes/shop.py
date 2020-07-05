from flask import request, abort, Response, flash

from .utils import *
from supermoms import app
from supermoms.auth.manage_user import user
from supermoms.auth.payment import create_payment, pop_payment, get_payment, complete_payment, refund_payment
from supermoms.auth.cart import *
from supermoms.database.products import Products, ProductOrders
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
    
    if product.members_only and not user.premium:
      flash(get_locale()['member_required'])
    
    bad = False
    
    if product.workshop: qty = 1
    else:
      try:
        qty = int(request.form['qty'])
      except ValueError:
        flash("Please enter a valid integer for the quantity!" if en() else "请输入一个整数！", "error")
        
        bad = True
     
    if not bad:

      if product.workshop and ci:
        if 'remove_cart' in request.form:
          CartItems.remove(ci)

          flash("You have been unregistered." if en() else "您的注册被取消了。", "success")
        else:        
          flash("You cannot register again! Proceed to checkout to confirm your registration." if en() else "您不可以再注册一遍！去结算以确认您的注册。", "error")

      elif product.workshop and (ProductOrders.query.filter_by(uid = user.id, pid = product.id).count() > 0):
        flash("You have already registered for this workshop!" if en() else "您已经注册了这个培训班！", "error")

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
          flash("You have been registered! You must checkout to confirm your registration." if en() else "注册成功！去结算以确认注册。", "success")

        else:
          flash("Items added to cart." if en() else "已加入购物车。", "success")
      
    # Get the cart item again cause it mightve been updated
    ci = CartItems.query.filter_by(uid = user.id, pid = id).first()
      
  registered = False
  cart = False
  not_member = False
  
  if product.members_only and (not user or not user.premium):
    not_member = True
  
  if product.workshop:
    if ci: cart = True
      
    if user and ProductOrders.query.filter_by(uid = user.id, pid = product.id).count() > 0: registered = True
        
  cur_qty = 0
  
  if ci: cur_qty = ci.count
  
  return render("product.html", p = product, cur_qty = cur_qty, desc = desc, name = name, cart = cart, 
                registered = registered, not_member = not_member)
  

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
      
      flash("Product deleted!" if en() else "已下架！", "success")
      
    else:
      workshop = 'workshop' in request.form

      p = Products.add(en_name = "", cn_name = "", en_desc = "", cn_desc = "", 
                       stock = 0, image = b"", member_price = 0.0, price = 0.0, workshop = workshop, hidden = True)

      return redirect("/admin/product/%d" % p.id, code = 303)
  
  products = Products.query.all()
  
  return render("admin/products.html", products = products)


@app.route("/admin/product/<int:id>", methods = ['GET', 'POST'])
@admin_auth
def serve_admin_product(id):  
  product = Products.query.filter_by(id = id).first_or_404();
  
  product_orders = ProductOrders.query.filter_by(pid = id).all()
        
  uids = [po.uid for po in product_orders]

  users = Users.query.filter(Users.id.in_(uids)).all()

  umap = {u.id : u for u in users}

  items = [(umap[po.uid], po) for po in product_orders]
    
  if request.method == "POST": 
    if "delete" in request.form:
      id = request.form['delete']
      
      ProductOrders.query.filter_by(id = id).delete()
      
      db_commit()
            
      if p.workshop:
        flash(get_locale()['workshop_order_deleted'], "success")
      else:
        flash(get_locale()['product_order_deleted'], "success")
      
      product_orders = ProductOrders.query.filter_by(pid = id).all()
      
      uids = [po.uid for po in product_orders]
      
      users = Users.query.filter(Users.id.in_(uids)).all()
      
      umap = {u.id : u for u in users}
      
      items = [(umap[po.uid], po) for po in product_orders]
      
    else:
      en_name = request.form['en_name']
      cn_name = request.form['cn_name']
    
      en_desc = request.form['en_desc']
      cn_desc = request.form['cn_desc']


      stock = request.form['stock']
      image = request.files['image'].read()
      
      price = request.form['price']
      member_price = request.form['member_price']
      
      hidden = 'publish' not in request.form
      members_only = 'members_only' in request.form
    
      bad = False
    
      try: 
        stock = int(stock)
      except ValueError:
        flash("Please enter a valid integer for the stock." if en() else "请输入一个整数。", "error")
  
        bad = True
      
      try: 
        price = float(price)
      except ValueError:
        flash("Please enter a valid number for the price." if en() else "请输入有效的价钱。", "error")

        bad = True
        
      try: 
        member_price = float(member_price)
      except ValueError:
        flash("Please enter a valid number for the price." if en() else "请输入有效的价钱。", "error")

        bad = True

      if len(en_name) > 1023 or len(cn_name) > 1023:
        flash("Product name too long!" if en() else "货品名字太长了！", "error")

        bad = True
      
      if type(price) == float and price < 0.5 and price != 0:
        flash("Price must be either at least 50 cents or free!" if en() else "价钱必须至少5毛或者免费！", "error")


      if len(en_desc) > 65535 or len(cn_desc) > 65535:
        flash("Product description too long!" if en() else "货品描述太长了！", "error")

      if len(image) > 2 ** 22:
        flash("Image too large! Maximum size is 4 MB!" if en() else "图片不能超过4MB！", "error")

      if not bad:
        product.stock = stock
        product.hidden = hidden

        if len(image) > 16: product.image = image

        product.en_name = en_name
        product.cn_name = cn_name

        product.en_desc = en_desc
        product.cn_desc = cn_desc

        product.price = price
        product.member_price = member_price
        
        product.members_only = members_only

        db_commit()

        flash("Product updated!" if en() else "货品已更新！", "success")
  
  return render("admin/edit_product.html", p = product, orders = items)

@app.route("/view-cart/", methods = ["GET", "POST"])
@authorize
def serve_view_cart():
  citems = CartItems.query.filter_by(uid = user.id).all()
  
  pids = [ci.pid for ci in citems]
  
  ps = Products.query.filter(Products.id.in_(pids)).all()
  
  pmap = {p.id : p for p in ps}
  
  items = [(pmap[ci.pid], ci) for ci in citems]
  
  if user.premium:
    total = sum(it[0].member_price * it[1].count for it in items)
  else:
    total = sum(it[0].price * it[1].count for it in items)
  
  if request.method == "POST":
    if not validate_cart():
      flash("Some items in your cart have since run out of stock. Your cart has been updated. We are sorry for the inconvenience." if en() else "购物车里的某些货品已售完。您的购物车已更新。见谅。", "error")
    
      citems = CartItems.query.filter_by(uid = user.id).all()
  
      pids = [ci.pid for ci in citems]

      ps = Products.query.filter(Products.id.in_(pids)).all()

      pmap = {p.id : p for p in ps}

      items = [(pmap[ci.pid], ci) for ci in citems]

      total = sum(it[0].price * it[1].count for it in items)
    
    else:
      # Calculate total amount
      amt = total

      create_payment(amt, "/confirm/checkout/")

      store_cart()

      if amt == 0: 
        complete_payment()

        return redirect("/confirm/checkout", code = 303)

      val = request.form['pay_method']

      if val == "paypal":
        return redirect('/pay/paypal', code = 303)

      return redirect('/pay/card', code = 303)
  
  return render("view_cart.html", items = items, total = total)


@app.route('/confirm/checkout/')
@authorize
def serve_checkout_confirm():
  pay_obj = pop_payment()
  
  if not check_cart_same():
    refund_payment(pay_obj)
    
    flash("Your cart has been modified since the payment session was initiated. Your payment has been cancelled." if en() else "从开始付款到现在购物车被更新。交易终止。", "error")
    
    return redirect('/view-cart/')
  
  if not validate_cart():
    refund_payment(pay_obj)

    flash("Some items in your cart have since run out of stock. Your cart has been updated. We are sorry for the inconvenience." if en() else "购物车里的某些货品已售完。您的购物车已更新。见谅。", "error")
        
    return redirect("/view-cart/")
  
  process_cart()
  
  flash("Your payment was processed and your items have been purchased. Thank you!" if en() else "交易成功。感谢惠顾！", "success")
  
  return redirect("/")