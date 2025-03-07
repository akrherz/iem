"""mod-wsgi service."""

import os

from TileCache.Service import Service

from iemweb.util import tms_handler

tilecachepath, wsgi_file = os.path.split(__file__)
cfgfiles = os.path.join(tilecachepath, "tilecache.cfg")
theService = {"app": None}


def application(environ, start_response):
    """Go service."""
    if not theService["app"]:
        theService["app"] = Service.load(cfgfiles)
    return tms_handler(environ, start_response, theService["app"])
