from supermoms import app

from supermoms.database.users import Users
from supermoms.server.routes import * # Resolve recursive import
from supermoms.utils.time import *

ct = get_time()

d30_list = Users.query.filter(30 * DAY <= Users.premium_end - ct, Users.premium_end - ct <= 31 * DAY).all()

d7_list = Users.query.filter(7 * DAY <= Users.premium_end - ct, Users.premium_end - ct <= 8 * DAY).all()

for u in d30_list:
  send_expiry_email(u.email, 30)
  
for u in d7_list:
  send_expiry_email(u.email, 7)