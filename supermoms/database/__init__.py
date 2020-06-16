from pharmacy import db

from .order_types import *
from .orders import *
from .product_types import *
from .products import *
from .users import *

db.create_all()