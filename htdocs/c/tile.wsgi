import os
import sys

def myexcepthook(exctype, value, traceback):
    if exctype == IOError:
        pass
    else:
        sys.__excepthook__(exctype, value, traceback)
sys.excepthook = myexcepthook

tilecachepath, wsgi_file = os.path.split(__file__)
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/include/python/')
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/include/python/TileCache/')

from TileCache.Service import Service, wsgiHandler
cfgfiles = (os.path.join(tilecachepath, "tilecache.cfg"))

theService = {}
def wsgiApp (environ, start_response):
    global theService

    cfgs  = cfgfiles
    if not theService:
        theService = Service.load(cfgs)
    return wsgiHandler(environ, start_response, theService)

application = wsgiApp