#!/usr/bin/env python
import sys
sys.path.append("/mesonet/www/apps/iemwebsite/include/python")
from TileCache import Service, cgiHandler, cfgfiles

if __name__ == '__main__':
    svc = Service.load(*cfgfiles)
    cgiHandler(svc)
