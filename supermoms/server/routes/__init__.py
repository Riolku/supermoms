# Import all routes into this file so that main.py can import them in one fell swoop.
# Otherwise the routes will never be registered

# import the utils since some of the functions need to be run
# import pharmacy.server.routes.utils

from pharmacy.server.routes.core import *