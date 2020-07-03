import threading

from supermoms import app, mail_app
from supermoms.server.routes.utils import get_lang
from supermoms.utils.files import load_file

from flask import request

from flask_mail import Message


EMAILS_EN = dict(
  login = dict(
    subject = "Login link for Super Moms Club Website",
    body = load_file("supermoms/mail/templates/en/login.txt")
  ),
  
  signup = dict(
    subject = "Signup link for Super Moms Club Website",
    body = load_file("supermoms/mail/templates/en/signup.txt")
  ),
  
  expiry = dict(
    subject = "Membership Expiry Notification for Super Moms Club Website",
    body = load_file("supermoms/mail/templates/en/expiry.txt")
  ),
)

EMAILS_CN = dict(
  login = dict(
    subject = "Super Moms Club网站登入链接",
    body = load_file("supermoms/mail/templates/cn/login.txt")
  ),
  
  signup = dict(
    subject = "Super Moms Club网站注册链接",
    body = load_file("supermoms/mail/templates/cn/signup.txt")
  )
)

def get_emails():
  if get_lang() == "CN":
    return EMAILS_CN
  else:
    return EMAILS_EN
  
def _inner_send_mail(to_addr, subject, content):
  mail_app.send_message(
    subject = subject,
    recipients = [to_addr],
    html = content
  )
  
def sync_send_mail(to_addr, subject, content):
  with app.app_context():
    _inner_send_mail(to_addr, subject, content)

def send_mail(to_addr, subject, content):
  threading.Thread(target = sync_send_mail, args = (to_addr, subject, content)).start()
  
def send_signin_email(to_addr, url):
  send_mail(to_addr, get_emails()['login']['subject'], get_emails()['login']['body'].format(url = url))
  
def send_signup_email(to_addr, url):
  send_mail(to_addr, get_emails()['signup']['subject'], get_emails()['signup']['body'].format(url = url))


def send_expiry_email(to_addr, days, lang, _inner = False, sync = True):
  em = (EMAILS_CN if lang == "CN" else EMAILS_EN)['expiry']


  daystr = str(days)
  if lang == "CN":
    pass # TODO: change to chinese numbers (idk, help)
    
  func = send_mail
  
  if _inner: func = _inner_send_mail
  elif sync: func = sync_send_mail
    
  func(to_addr, em['subject'], em['body'].format(days = daystr))

