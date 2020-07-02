# Import all routes into this file so that main.py can import them in one fell swoop.
# Otherwise the routes will never be registered

import supermoms.server.routes.core
import supermoms.server.routes.utils
import supermoms.server.routes.payment
import supermoms.server.routes.errors