#!/usr/bin/python
import copy
import re
import sys, cgi, time, os, traceback, email, ConfigParser
import Cache, Caches
import Layer, Layers
import datetime

# BSD Licensed, Copyright (c) 2006-2010 TileCache Contributors

class TileCacheException(Exception): pass

class TileCacheLayerNotFoundException(Exception):
    pass

class TileCacheFutureException(Exception):
    pass


# Windows doesn't always do the 'working directory' check correctly.
if sys.platform == 'win32':
    workingdir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
    cfgfiles = (os.path.join(workingdir, "tilecache.cfg"), os.path.join(workingdir,"..","tilecache.cfg"))
else:
    cfgfiles = ("/etc/tilecache.cfg", os.path.join("..", "tilecache.cfg"), "tilecache.cfg")


class Capabilities (object):
    def __init__ (self, format, data):
        self.format = format
        self.data   = data


class Request (object):
    def __init__(self, service):
        self.service = service

    def getLayer(self, layername):
        """implements some custom logic here for the provided layername"""
        if layername.startswith('idep'):
            (lbl, ltype, date) = layername.split("::", 3)
            scenario = lbl[4:]
            uri = ('date=%s&year=%s&month=%s&day=%s&scenario=%s'
                   ) % (date, date[:4], date[5:7], date[8:10], scenario)
            layer = copy.copy(self.service.layers['idep'])
            layer.name = layername
            layer.layers = ltype
            layer.url = "%s%s" % (layer.metadata['baseurl'], uri)
        elif layername.startswith('goes::'):
            (bird, channel, tstring) = (layername.split("::")[1]).split('-')
            if len(tstring) == 12:
                mylayername = 'goes-t'
                year = tstring[:4]
                month = tstring[4:6]
                day = tstring[6:8]
                ts = tstring[8:12]
                uri = "year=%s&month=%s&day=%s&time=%s&" % (year,
                                                            month, day, ts)
            else:
                mylayername = 'goes'
                uri = ''
            layer = copy.copy(self.service.layers[mylayername])
            layer.name = layername
            layer.url = "%sbird=%s&channel=%s&%s" % (
                layer.metadata['baseurl'], bird, channel, uri)
        elif layername.startswith('hrrr::'):
            (prod, ftime, tstring) = (layername.split("::")[1]).split('-')
            if len(tstring) == 12:
                mylayername = 'hrrr-refd-t'
                mslayer = 'refd-t'
                year = tstring[:4]
                month = tstring[4:6]
                day = tstring[6:8]
                hour = tstring[8:10]
                uri = ("year=%s&month=%s&day=%s&hour=%s&f=%s"
                       ) % (year, month, day, hour, ftime[1:])
            else:
                mylayername = 'hrrr-refd'
                mslayer = 'refd_%s' % (ftime[1:], )
                uri = ''
            layer = copy.copy(self.service.layers[mylayername])
            layer.name = mslayer
            layer.url = "%s%s" % (layer.metadata['baseurl'], uri)
        elif layername.find("::") > 0:
            (sector, prod, tstring) = (layername.split("::")[1]).split('-')
            if len(tstring) == 12:
                utcnow = (datetime.datetime.utcnow() +
                          datetime.timedelta(minutes=5)).strftime("%Y%m%d%H%M")
                if tstring > utcnow:
                    raise TileCacheFutureException(
                        "Specified time in the future!")
                mylayername = 'ridge-t'
                year = tstring[:4]
                month = tstring[4:6]
                day = tstring[6:8]
                ts = tstring[8:12]
                if sector in ['USCOMP', 'HICOMP', 'AKCOMP', 'PRCOMP']:
                    mylayername = 'ridge-composite-t'
                    if prod == 'N0R':
                        mylayername = 'ridge-composite-t-n0r'
                    sector = sector.lower()
                    prod = prod.lower()
                    # these should always be for a minutes mod 5
                    # if not, save the users from themselves
                    if ts[-1] not in ["0", "5"]:
                        extra = "5" if ts[-1] > "5" else "0"
                        ts = "%s%s" % (ts[:3], extra)
                uri = "year=%s&month=%s&day=%s&time=%s&" % (year,
                                                            month, day, ts)
            else:
                if sector in ['USCOMP', 'HICOMP', 'AKCOMP', 'PRCOMP']:
                    prod = prod.lower()
                    mylayername = 'ridge-composite-single'
                else:
                    mylayername = 'ridge-single'
                uri = ''
            layer = copy.copy(self.service.layers[mylayername])
            layer.name = layername
            layer.url = "%ssector=%s&prod=%s&%s" % (layer.metadata['baseurl'],
                                                    sector, prod, uri)
        else:
            layer = self.service.layers.get(layername, None)
            if layer is None:
                raise TileCacheLayerNotFoundException(("Layer %s not found"
                                                       ) % (layername,))
        return layer


def import_module(name):
    """Helper module to import any module based on a name, and return the module."""
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class Service (object):
    __slots__ = ("layers", "cache", "metadata", "tilecache_options", "config", "files")

    def __init__ (self, cache, layers, metadata = {}):
        self.cache    = cache
        self.layers   = layers
        self.metadata = metadata
 
    def _loadFromSection (cls, config, section, module, **objargs):
        type  = config.get(section, "type")
        for opt in config.options(section):
            if opt not in ["type", "module"]:
                objargs[opt] = config.get(section, opt)
        
        object_module = None
        
        if config.has_option(section, "module"):
            object_module = import_module(config.get(section, "module"))
        else: 
            if module is Layer:
                type = type.replace("Layer", "")
                object_module = import_module("TileCache.Layers.%s" % type)
            else:
                type = type.replace("Cache", "")
                object_module = import_module("TileCache.Caches.%s" % type)
        if object_module == None:
            raise TileCacheException("Attempt to load %s failed." % type)
        
        section_object = getattr(object_module, type)
        
        if module is Layer:
            return section_object(section, **objargs)
        else:
            return section_object(**objargs)
    loadFromSection = classmethod(_loadFromSection)

    def _load (cls, *files):
        cache = None
        metadata = {}
        layers = {}
        config = None
        try:
            config = ConfigParser.ConfigParser()
            config.read(files)
            
            if config.has_section("metadata"):
                for key in config.options("metadata"):
                    metadata[key] = config.get("metadata", key)
            
            if config.has_section("tilecache_options"):
                if 'path' in config.options("tilecache_options"): 
                    for path in config.get("tilecache_options", "path").split(","):
                        sys.path.insert(0, path)
            
            cache = cls.loadFromSection(config, "cache", Cache)

            layers = {}
            for section in config.sections():
                if section in cls.__slots__: continue
                layers[section] = cls.loadFromSection(
                                        config, section, Layer, 
                                        cache = cache)
        except Exception, E:
            metadata['exception'] = E
            metadata['traceback'] = "".join(traceback.format_tb(sys.exc_traceback))
        service = cls(cache, layers, metadata)
        service.files = files
        service.config = config
        return service 
    load = classmethod(_load)

    def generate_crossdomain_xml(self):
        """Helper method for generating the XML content for a crossdomain.xml
           file, to be used to allow remote sites to access this content."""
        xml = ["""<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM
  "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
        """]
        if self.metadata.has_key('crossdomain_sites'):
            sites = self.metadata['crossdomain_sites'].split(',')
            for site in sites:
                xml.append('  <allow-access-from domain="%s" />' % site)
        xml.append("</cross-domain-policy>")        
        return ('text/xml', "\n".join(xml))       

    def renderTile(self, tile, force=False):
        """render a Tile please"""
        layer = tile.layer
        if layer.debug:
            start = time.time()

        # do more cache checking here: SRS, width, height, layers

        image = None
        if not force:
            image = self.cache.get(tile)
        if not image:
            data = layer.render(tile, force=force)
            if data:
                image = self.cache.set(tile, data)
            else:
                raise Exception("Zero length data returned from layer.")
            if layer.debug:
                sys.stderr.write(("Cache miss: %s, Tile: x: %s, y: %s, z: %s, "
                                  "time: %s\n"
                                  ) % (tile.bbox(), tile.x, tile.y, tile.z,
                                       (time.time() - start)))
        else:
            if layer.debug:
                sys.stderr.write(("Cache hit: %s, Tile: x: %s, y: %s, z: %s, "
                                  "time: %s, debug: %s\n"
                                  ) % (tile.bbox(), tile.x, tile.y, tile.z,
                                       (time.time() - start), layer.debug))

        return (layer.mime_type, image)

    def expireTile (self, tile):
        bbox  = tile.bounds()
        layer = tile.layer 
        for z in range(len(layer.resolutions)):
            bottomleft = layer.getClosestCell(z, bbox[0:2])
            topright   = layer.getClosestCell(z, bbox[2:4])
            for y in range(bottomleft[1], topright[1] + 1):
                for x in range(bottomleft[0], topright[0] + 1):
                    coverage = Layer.Tile(layer,x,y,z)
                    self.cache.delete(coverage)

    def dispatchRequest(self, params, path_info="/", req_method="GET",
                        host="http://example.com/"):
        """dispatch the request!"""
        if 'exception' in self.metadata:
            raise TileCacheException("%s\n%s" % (self.metadata['exception'],
                                                 self.metadata['traceback']))
        if path_info.find("crossdomain.xml") != -1:
            return self.generate_crossdomain_xml()

        if path_info.split(".")[-1] == "kml":
            from TileCache.Services.KML import KML
            return KML(self).parse(params, path_info, host)

        # A shortcut for the most common usage case of a TMS call
        # any empty dict is False
        if bool(params) is False:
            from TileCache.Services.TMS import TMS
            tile = TMS(self).parse(params, path_info, host)
        elif "scale" in params or "SCALE" in params:
            from TileCache.Services.WMTS import WMTS
            tile = WMTS(self).parse(params, path_info, host)
        elif ("service" in params or "SERVICE" in params or
                "REQUEST" in params and params['REQUEST'] == "GetMap" or
                "request" in params and params['request'] == "GetMap"):
            from TileCache.Services.WMS import WMS
            tile = WMS(self).parse(params, path_info, host)
        elif ("L" in params or "l" in params or
                "request" in params and params['request'] == "metadata"):
            from TileCache.Services.WorldWind import WorldWind
            tile = WorldWind(self).parse(params, path_info, host)
        elif "interface" in params:
            from TileCache.Services.TileService import TileService
            tile = TileService(self).parse(params, path_info, host)
        elif ("v" in params and
                (params['v'] == "mgm" or params['v'] == "mgmaps")):
            from TileCache.Services.MGMaps import MGMaps
            tile = MGMaps(self).parse(params, path_info, host)
        elif "tile" in params:
            from TileCache.Services.VETMS import VETMS
            tile = VETMS(self).parse(params, path_info, host)
        elif "format" in params and params['format'].lower() == "json":
            from TileCache.Services.JSON import JSON
            return JSON(self).parse(params, path_info, host)
        else:
            from TileCache.Services.TMS import TMS
            tile = TMS(self).parse(params, path_info, host)

        if isinstance(tile, Layer.Tile):
            if req_method == 'DELETE':
                self.expireTile(tile)
                return ('text/plain', 'OK')
            else:
                return self.renderTile(tile, 'FORCE' in params)
        elif isinstance(tile, list):
            if req_method == 'DELETE':
                [self.expireTile(t) for t in tile]
                return ('text/plain', 'OK')
            else:
                try:
                    import PIL.Image as Image
                except ImportError:
                    raise Exception("Combining multiple layers requires Python Imaging Library.")
                try:
                    import cStringIO as StringIO
                except ImportError:
                    import StringIO

                result = None

                for t in tile:
                    (format, data) = self.renderTile(t, params.has_key('FORCE'))
                    image = Image.open(StringIO.StringIO(data))
                    if not result:
                        result = image
                    else:
                        try:
                            result.paste(image, None, image)
                        except Exception, E:
                            raise Exception("Could not combine images: Is it possible that some layers are not \n8-bit transparent images? \n(Error was: %s)" % E) 

                buffer = StringIO.StringIO()
                result.save(buffer, result.format)
                buffer.seek(0)

                return (format, buffer.read())
        else:
            return (tile.format, tile.data)


def modPythonHandler(apacheReq, service):
    from mod_python import apache, util
    try:
        if "X-Forwarded-Host" in apacheReq.headers_in:
            host = "http://" + apacheReq.headers_in["X-Forwarded-Host"]
        else:
            host = "http://" + apacheReq.headers_in["Host"]
        host += apacheReq.uri[:-len(apacheReq.path_info)]
        fmt, image = service.dispatchRequest(util.FieldStorage(apacheReq),
                                             apacheReq.path_info,
                                             apacheReq.method,
                                             host)
        apacheReq.content_type = fmt
        apacheReq.status = apache.HTTP_OK
        if format.startswith("image/"):
            if service.cache.sendfile:
                apacheReq.headers_out['X-SendFile'] = image
            if service.cache.expire:
                apacheReq.headers_out['Expires'] = email.Utils.formatdate(
                    time.time() + service.cache.expire, False, True)

        apacheReq.set_content_length(len(image))
        apacheReq.send_http_header()
        if format.startswith("image/") and service.cache.sendfile:
            apacheReq.write("")
        else:
            apacheReq.write(image)
    except IOError, E:
        pass
    except TileCacheException, E:
        apacheReq.content_type = "text/plain"
        apacheReq.status = apache.HTTP_NOT_FOUND
        apacheReq.send_http_header()
        apacheReq.write("An error occurred: %s\n" % (str(E)))
    except Exception, E:
        apache.log_error("TCError: %s %s" % (str(E), apacheReq.uri),
                         apache.APLOG_ERR)
        apacheReq.content_type = "text/plain"
        apacheReq.status = apache.HTTP_INTERNAL_SERVER_ERROR
        apacheReq.send_http_header()
        try:
            apacheReq.write("An error occurred: %s\n%s\n" % (
                str(E),
                "".join(traceback.format_tb(sys.exc_traceback))))
        except:
            pass
    return apache.OK


def wsgiHandler(environ, start_response, service):
    """ This is the WSGI handler """
    from paste.request import parse_formvars
    host = ""
    path_info = environ.get("PATH_INFO", "")

    if "HTTP_X_FORWARDED_HOST" in environ:
        host = "http://" + environ["HTTP_X_FORWARDED_HOST"]
    elif "HTTP_HOST" in environ:
        host = "http://" + environ["HTTP_HOST"]

    host += environ["SCRIPT_NAME"]
    req_method = environ["REQUEST_METHOD"]
    try:
        fields = parse_formvars(environ)

        fmt, image = service.dispatchRequest(fields,
                                             path_info, req_method, host)
        headers = [('Content-Type', fmt)]
        if fmt.startswith("image/"):
            if service.cache.sendfile:
                headers.append(('X-SendFile', image))
            if service.cache.expire:
                headers.append(('Expires', email.Utils.formatdate(
                                time.time() + service.cache.expire,
                                False, True)))

        start_response("200 OK", headers)
        if service.cache.sendfile and fmt.startswith("image/"):
            return []
        else:
            return [image]

    except TileCacheException, E:
        status = '404 Tile Not Found'
        msg = "An error occurred: %s" % (str(E),)
    except TileCacheLayerNotFoundException, E:
        status = "500 Internal Server Error"
        msg = "%s" % (str(E),)
    except TileCacheFutureException, E:
        status = "500 Internal Server Error"
        msg = "%s" % (str(E),)
    except Exception, E:
        status = "500 Internal Server Error"
        E = str(E)
        # Swallow this error
        if E.find("Corrupt, empty or missing file") == -1:
            sys.stderr.write(("[client: %s] Path: %s Err: %s Referrer: %s\n"
                              ) % (environ.get("REMOTE_ADDR"), path_info,
                                   E.replace("\n", " "),
                                   environ.get("HTTP_REFERER")))
        # nice code, but we are getting invalid requests into the near future
        # which error out.
        # else:
        #    missfn = ""
        #    f = re.search("/mesonet/ARCHIVE/data/(?P<a>[a-zA-Z0-9/\._\-]+)&",
        #                  E)
        #    if f:
        #        missfn = f.groupdict()['a']
        #    sys.stderr.write(("[client: %s] Path: %s errored with "
        #                      "missing file %s Referrer: %s\n"
        #                      ) % (environ.get("REMOTE_ADDR"), path_info,
        #                           missfn, environ.get("HTTP_REFERER")))
        msg = ("An error occurred: %s\n"
               ) % (E, )

    start_response(status, [('Content-Type', 'text/plain')])
    return [msg]


def cgiHandler(service):
    try:
        params = {}
        input = cgi.FieldStorage()
        for key in input.keys(): params[key] = input[key].value
        path_info = host = ""

        if "PATH_INFO" in os.environ: 
            path_info = os.environ["PATH_INFO"]

        if "HTTP_X_FORWARDED_HOST" in os.environ:
            host      = "http://" + os.environ["HTTP_X_FORWARDED_HOST"]
        elif "HTTP_HOST" in os.environ:
            host      = "http://" + os.environ["HTTP_HOST"]

        host += os.environ["SCRIPT_NAME"]
        req_method = os.environ["REQUEST_METHOD"]
        format, image = service.dispatchRequest( params, path_info, req_method, host )
        print "Content-type: %s" % format
        if format.startswith("image/"):
            if service.cache.sendfile:
                print "X-SendFile: %s" % image
            if service.cache.expire:
                print "Expires: %s" % email.Utils.formatdate(time.time() + service.cache.expire, False, True)
        print ""
        if (not service.cache.sendfile) or (not format.startswith("image/")):
            if sys.platform == "win32":
                binaryPrint(image)
            else:    
                print image
    except TileCacheException, E:
        print "Cache-Control: max-age=10, must-revalidate" # make the client reload        
        print "Content-type: text/plain\n"
        print "An error occurred: %s\n" % (str(E))
    except Exception, E:
        print "Cache-Control: max-age=10, must-revalidate" # make the client reload        
        print "Content-type: text/plain\n"
        print "An error occurred: %s\n%s\n" % (
            str(E), 
            "".join(traceback.format_tb(sys.exc_traceback)))

theService = {}
lastRead = {}
def handler (apacheReq):
    global theService, lastRead
    options = apacheReq.get_options()
    cfgs    = cfgfiles
    fileChanged = False
    if options.has_key("TileCacheConfig"):
        configFile = options["TileCacheConfig"]
        lastRead[configFile] = time.time()
        
        cfgs = cfgs + (configFile,)
        try:
            cfgTime = os.stat(configFile)[8]
            fileChanged = lastRead[configFile] < cfgTime
        except:
            pass
    else:
        configFile = 'default'
        
    if not theService.has_key(configFile) or fileChanged:
        theService[configFile] = Service.load(*cfgs)
        
    return modPythonHandler(apacheReq, theService[configFile])

def wsgiApp (environ, start_response):
    global theService
    cfgs    = cfgfiles
    if not theService:
        theService = Service.load(*cfgs)
    return wsgiHandler(environ, start_response, theService)

def binaryPrint(binary_data):
    """This function is designed to work around the fact that Python
       in Windows does not handle binary output correctly. This function
       will set the output to binary, and then write to stdout directly
       rather than using print."""
    try:
        import msvcrt
        msvcrt.setmode(sys.__stdout__.fileno(), os.O_BINARY)
    except:
        pass
    sys.stdout.write(binary_data)    

def paste_deploy_app(global_conf, full_stack=True, **app_conf):
    if 'tilecache_config' in app_conf:
        cfgfiles = (app_conf['tilecache_config'],)
    else:
        raise TileCacheException("No tilecache_config key found in configuration. Please specify location of tilecache config file in your ini file.")
    theService = Service.load(*cfgfiles)
    if 'exception' in theService.metadata:
        raise theService.metadata['exception']
    
    def pdWsgiApp (environ,start_response):
        return wsgiHandler(environ,start_response,theService)
    
    return pdWsgiApp

if __name__ == '__main__':
    svc = Service.load(*cfgfiles)
    cgiHandler(svc)
