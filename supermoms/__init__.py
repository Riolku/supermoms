from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

from .config import configure_app

app = Flask("supermoms")

app = configure_app(app)

db = SQLAlchemy(app)

mail_app = Mail(app)