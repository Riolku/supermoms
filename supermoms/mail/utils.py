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
#    body = load_file("supermoms/mail/templates/en/expiry.txt")
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

def send_mail(to_addr, subject, content):
  def inner():
    with app.app_context():
      mail_app.send_message(
        subject = subject,
        recipients = [to_addr],
        html = content
      )
    
  threading.Thread(target = inner).start()
  
def send_signin_email(to_addr, url):
  send_mail(to_addr, get_emails()['login']['subject'], get_emails()['login']['body'].format(url = url))
  
def send_signup_email(to_addr, url):
  send_mail(to_addr, get_emails()['signup']['subject'], get_emails()['signup']['body'].format(url = url))