"""
 This is mod_python magic with the help of what is in .htaccess
"""
from TileCache import Service, cgiHandler, cfgfiles

if __name__ == '__main__':
    svc = Service.load(*cfgfiles)
    cgiHandler(svc)
