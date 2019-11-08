"""mod-wsgi service."""
import os

# https://github.com/akrherz/tilecache
from TileCache.Service import Service, wsgiHandler

tilecachepath, wsgi_file = os.path.split(__file__)
cfgfiles = os.path.join(tilecachepath, "tilecache.cfg")
theService = {"app": None}


def application(environ, start_response):
    """Go service."""
    if not theService["app"]:
        theService["app"] = Service.load(cfgfiles)
    return wsgiHandler(environ, start_response, theService["app"])
