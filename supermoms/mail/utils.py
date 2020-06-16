import threading

from supermoms import mail_app

from supermoms.utils.files import load_file

EMAILS = dict(
  login = dict(
    subject = "Login link for Super Moms Club Website",
    body = load_file("supermoms/mail/templates/login.txt")
  ),
  
  signup = dict(
    subject = "Signup link for Super Moms Club Website",
    body = load_file("supermoms/mail/templates/signup.txt")
  )
)

def send_mail(to_addr, subject, content):
  def inner():
    mail_app.send_message(Message(
      subject = subject,
      recipients = to_addr,
      html = content
    ))
    
  threading.Thread(target = inner).start()
  
def send_email_login(to_addr, url):
  send_mail(to_addr, EMAILS['login']['subject'], EMAILS['login']['body'].format(url = url))
  
def send_signup_email(to_addr, url):
  send_mail(to_addr, EMAILS['signup']['subject'], EMAILS['signup']['body'].format(url = url))