import os
import sys

tilecachepath, wsgi_file = os.path.split(__file__)
sys.path.insert(0, "/opt/iem/include/python/")
sys.path.insert(0, "/opt/iem/include/python/TileCache/")

from TileCache.Service import Service, wsgiHandler

cfgfiles = os.path.join(tilecachepath, "tilecache.cfg")

theService = {}


def wsgiApp(environ, start_response):
    global theService

    cfgs = cfgfiles
    if not theService:
        theService = Service.load(cfgs)
    return wsgiHandler(environ, start_response, theService)


application = wsgiApp
