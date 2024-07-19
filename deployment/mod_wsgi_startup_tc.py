"""Invoked at mod-wsgi startup for tc services."""

import sys

# Have our local pylib module as the first place to look
if "/opt/iem/pylib" not in sys.path:
    sys.path.insert(0, "/opt/iem/pylib")
