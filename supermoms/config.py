import os, stripe

from sys import argv

from .utils.files import load_json
from werkzeug.middleware.proxy_fix import ProxyFix 

stripe_pkey = None

paypal_pkey = None
paypal_skey = None
paypal_base_url = None

def configure_app(application):
  global stripe_pkey, paypal_skey, paypal_pkey, paypal_base_url
  
  keys = load_json(os.environ['TALENTMAKER_KEYS_FILE'])
  
  
  stripe_pkey = keys['STRIPE_PKEY']
  stripe.api_key = keys['STRIPE_SKEY']
  
  paypal_pkey = keys['PAYPAL_PKEY']
  paypal_skey = keys['PAYPAL_SKEY']
  
  paypal_base_url = keys['PAYPAL_BASE_URL']
  
  
  application.secret_key = keys['SECRET_KEY']
  
  application.debug = True
  
  app_config = dict(
    
    SQLALCHEMY_DATABASE_URI = keys['DATABASE_URI'],
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    
    COOKIES_SECURE = True,
    COOKIES_HTTPONLY = True,
    
    PREFERRED_URL_SCHEME = "https",
    
    TRAP_BAD_REQUEST_ERRORS = True,
    
    SERVER_NAME = keys['SERVER_NAME'],
    
    MAIL_SERVER = keys["MAIL_SERVER"],
    MAIL_USE_TLS = True,
    MAIL_PORT = keys['MAIL_PORT'],
    MAIL_USERNAME = keys.get('MAIL_USERNAME'),
    MAIL_PASSWORD = keys.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = tuple(keys['MAIL_SENDER']),
    
    ALT_PORT = 'alt' in argv
  )
  
  if app_config['ALT_PORT']:
    app_config['SERVER_NAME'] = keys['ALT_SERVER_NAME']
  
  application.config.update(app_config)
  
  application.wsgi_app = ProxyFix(application.wsgi_app, x_for = 1, x_proto = 1, x_port = 1, x_host = 1)
    
  return application