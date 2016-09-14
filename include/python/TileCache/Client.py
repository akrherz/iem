#!/usr/bin/env python

# BSD Licensed, Copyright (c) 2006-2010 TileCache Contributors

import sys, urllib, urllib2, time, os, math
import time
import httplib
try:
    from optparse import OptionParser
except ImportError:
    OptionParser = False 

# setting this to True will exchange more useful error messages
# for privacy, hiding URLs and error messages.
HIDE_ALL = False 

class WMS (object):
    fields = ("bbox", "srs", "width", "height", "format", "layers", "styles")
    defaultParams = {'version': '1.1.1', 'request': 'GetMap', 'service': 'WMS'}
    __slots__ = ("base", "params", "client", "data", "response")

    def __init__ (self, base, params, user=None, password=None):
        self.base    = base
        if self.base[-1] not in "?&":
            if "?" in self.base:
                self.base += "&"
            else:
                self.base += "?"

        self.params  = {}
        if user is not None and password is not None:
           x = urllib2.HTTPPasswordMgrWithDefaultRealm()
           x.add_password(None, base, user, password)
           self.client  = urllib2.build_opener()
           auth = urllib2.HTTPBasicAuthHandler(x)
           self.client  = urllib2.build_opener(auth)
        else:
           self.client  = urllib2.build_opener()

        for key, val in self.defaultParams.items():
            if self.base.lower().rfind("%s=" % key.lower()) == -1:
                self.params[key] = val
        for key in self.fields:
            if params.has_key(key):
                self.params[key] = params[key]
            elif self.base.lower().rfind("%s=" % key.lower()) == -1:
                self.params[key] = ""

    def url (self):
        return self.base + urllib.urlencode(self.params)

    def fetch(self):
        """Fetch image from backend"""
        urlrequest = urllib2.Request(self.url())
        response = self.client.open(urlrequest)
        data = response.read()
        # check to make sure that we have an image...
        msg = response.info()
        ctype = msg.get('Content-Type', '')
        if ctype[:5].lower() != 'image':
            if HIDE_ALL:
                raise Exception(("Did not get image data back. "
                                 "(Adjust HIDE_ALL for more detail.)"))
            else:
                raise Exception(("Did not get image data back. \n"
                                 "URL: %s\nContent-Type Header: %s\n"
                                 "Response: \n%s") % (self.url(), ctype, data))
        return data, response

    def setBBox (self, box):
        self.params["bbox"] = ",".join(map(str, box))

def seed (svc, layer, levels = (0, 5), bbox = None, padding = 0, force = False, reverse = False, delay = 0 ):
    from Layer import Tile
    try:
        padding = int(padding)
    except:
        raise Exception('Your padding parameter is %s, but should be an integer' % padding)

    if not bbox: bbox = layer.bbox

    start = time.time()
    total = 0
    
    for z in range(*levels):
        bottomleft = layer.getClosestCell(z, bbox[0:2])
        topright   = layer.getClosestCell(z, bbox[2:4])
        # Why Are we printing to sys.stderr??? It's not an error.
        # This causes a termination if run from cron or in background if shell is terminated
        #print >>sys.stderr, "###### %s, %s" % (bottomleft, topright)
        print "###### %s, %s" % (bottomleft, topright)
        zcount = 0 
        metaSize = layer.getMetaSize(z)
        ztiles = int(math.ceil(float(topright[1] - bottomleft[1]) / metaSize[0]) * math.ceil(float(topright[0] - bottomleft[0]) / metaSize[1]))
        if reverse:
            startX = topright[0] + metaSize[0] + (1 * padding)
            endX = bottomleft[0] - (1 * padding)
            stepX = -metaSize[0]
            startY = topright[1] + metaSize[1] + (1 * padding)
            endY = bottomleft[1] - (1 * padding)
            stepY = -metaSize[1]
        else:
            startX = bottomleft[0] - (1 * padding)
            endX = topright[0] + metaSize[0] + (1 * padding)
            stepX = metaSize[0]
            startY = bottomleft[1] - (1 * padding)
            endY = topright[1] + metaSize[1] + (1 * padding)
            stepY = metaSize[1]
        for y in range(startY, endY, stepY):
            for x in range(startX, endX, stepX):
                tileStart = time.time()
                tile = Tile(layer,x,y,z)
                bounds = tile.bounds()
                svc.renderTile(tile,force=force)
                total += 1
                zcount += 1
                box = "(%.4f %.4f %.4f %.4f)" % bounds
                print "%02d (%06d, %06d) = %s [%.4fs : %.3f/s] %s/%s" \
                     % (z,x,y, box, time.time() - tileStart, total / (time.time() - start + .0001), zcount, ztiles)
                if delay:
                    time.sleep(delay)

def main ():
    if not OptionParser:
        raise Exception("TileCache seeding requires optparse/OptionParser. Your Python may be too old.\nSend email to the mailing list \n(http://openlayers.org/mailman/listinfo/tilecache) about this problem for help.")
    usage = "usage: %prog <layer> [<zoom start> <zoom stop>]"
    
    parser = OptionParser(usage=usage, version="%prog $Id: Client.py 406 2010-10-15 11:00:18Z crschmidt $")
    
    parser.add_option("-f","--force", action="store_true", dest="force", default = False,
                      help="force recreation of tiles even if they are already in cache")
    
    parser.add_option("-b","--bbox",action="store", type="string", dest="bbox", default = None,
                      help="restrict to specified bounding box")
    parser.add_option("-c", "--config", action="store", type="string", dest="tilecacheconfig", 
        default=None, help="path to configuration file")                 
    parser.add_option("-d","--delay",action="store", type="int", dest="delay", default = 0,
        help="Delay time between requests.")
    parser.add_option("-p","--padding",action="store", type="int", dest="padding", default = 0,
                      help="extra margin tiles to seed around target area. Defaults to 0 "+
                      "(some edge tiles might be missing).      A value of 1 ensures all tiles "+
                      "will be created, but some tiles may be wholly outside your bbox")
   
    parser.add_option("-r","--reverse", action="store_true", dest="reverse", default = False,
                      help="Reverse order of seeding tiles")
    
    (options, args) = parser.parse_args()
    
    if len(args)>3:
        parser.error("Incorrect number of arguments. bbox and padding are now options (-b and -p)")

    from Service import Service, cfgfiles
    from Layer import Layer
    cfgs = cfgfiles
    if options.tilecacheconfig:
        configFile = options.tilecacheconfig
        print "Config file set to %s" % (configFile)
        cfgs = cfgs + (configFile,)
 
    svc = Service.load(*cfgs)

    layer = svc.layers[args[0]]
    
    if options.bbox:
        bboxlist = map(float,options.bbox.split(","))
    else:
        bboxlist=None
    
        
    if len(args)>1:    
        seed(svc, layer, map(int, args[1:3]), bboxlist , padding=options.padding, force = options.force, reverse = options.reverse, delay=options.delay)
    else:
        for line in sys.stdin.readlines():
            lat, lon, delta = map(float, line.split(","))
            bbox = (lon - delta, lat - delta, lon + delta, lat + delta)
            print "===> %s <===" % (bbox,)
            seed(svc, layer, (5, 17), bbox , force = options.force )

if __name__ == '__main__':
    main()
