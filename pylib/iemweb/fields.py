"""Stanardized fields used as parameters in Models.

So we have a convoluted set of things to support here, depending on if the
field has a None default or not.  So we have three scenarios supported by
the two field combinations, i.e. FIELD and FIELD_OPTIONAL.

    1. Parameter is always required -> `name: FIELD`
    2. Parameter has a default of proper type -> `name: FIELD = "good"`
    3. Parameter is not required and None by default
       -> `name: FIELD_OPTIONAL = None`

"""

# Shim until everything migrates to pyiem API
from pyiem.web.fields import *  # noqa
