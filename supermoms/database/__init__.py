from supermoms import db

from .blog import *
from .cart_items import *
from .products import *
from .users import *

db.create_all()