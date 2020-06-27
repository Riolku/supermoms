import requests

from supermoms.utils.time import get_time
from supermoms.server.routes.utils import get_lang

from supermoms.config import paypal_pkey, paypal_skey, paypal_base_url

from supermoms import app

cur_token = None
expire = 0

def paypal_url(path):
  return paypal_base_url + path

def get_access_token():
  global expire, cur_token
  
  if expire < get_time():
    
    res = requests.post(paypal_url("/v1/oauth2/token"), headers = {
      "Accept" : "application/json",
      "Accept-Language" : "en_US",
    }, auth = (paypal_pkey, paypal_skey), data = dict(grant_type = "client_credentials"))
    
    assert res.status_code == 200
    
    j = res.json()
    
    cur_token = j['access_token']
    expire = get_time() + j['expires_in'] - 60 # 1 minute grace to make sure our tokebn doesn't get rejected
    
  return cur_token

def create_order(amount, **k):
  
  reqj = dict(
    intent = "CAPTURE",
    purchase_units = [dict(
      amount = dict(
        currency_code = "CAD",
        value = amount
      )
    )],
    application_context = dict(
      locale = "zh-CN" if get_lang() == "CN" else "en-CA",
      landing_page = "LOGIN",
      shipping_preference = "NO_SHIPPING",
      user_action = "PAY_NOW",
      return_url = "https://" + app.config['SERVER_NAME'] + "/pay/paypal/confirm",
      cancel_url = "https://" + app.config['SERVER_NAME'] + "/pay/paypal/cancel",
      brand_name = "Super Moms Club"
    )
  )
  
  reqj.update(k)
  
  res = requests.post(paypal_url("/v2/checkout/orders"), headers = dict(
    Authorization = "Bearer " + get_access_token()
  ), json = reqj)
  
  
  assert res.status_code == 201
  
  j = res.json()
  
  links = j['links']
  
  approve = None
  
  for l in links:
    if l['rel'] == 'approve':
      assert l['method'] == 'GET'
      
      return l['href']
    
  raise ValueError("Could not find an appropriate link:" + str(j))
  
def confirm_order(id):
  print(id)
  
  res = requests.post(paypal_url("/v2/checkout/orders/{id}/capture".format(id = id)), json = {}, headers = dict(
    Authorization = "Bearer " + get_access_token()
  ))
  
  print(res, res.status_code)
  
  assert res.status_code == 201