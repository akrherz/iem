"""mod_wsgi handler for autoplot cache needs"""
import sys
import imp
import os
import json

from paste.request import parse_formvars
from pyiem.util import get_dbconn

BASEDIR, WSGI_FILENAME = os.path.split(__file__)
if BASEDIR not in sys.path:
    sys.path.insert(0, BASEDIR)


def get_timing(pidx):
    """Return an average plot generation time for this app"""
    pgconn = get_dbconn('mesosite')
    cursor = pgconn.cursor()
    cursor.execute("""
        SELECT avg(timing) from autoplot_timing where appid = %s
        and valid > (now() - '7 days'::interval)
    """, (pidx, ))
    timing = cursor.fetchone()[0]
    return timing if timing is not None else -1


def application(environ, start_response):
    """Our Application!"""
    fields = parse_formvars(environ)
    pidx = int(fields.get('p', 0))
    status = '200 OK'

    if pidx == 0:
        import scripts  # @UnresolvedImport
        data = scripts.data
    else:
        if pidx >= 100:
            name = 'scripts100/p%s' % (pidx, )
        else:
            name = 'scripts/p%s' % (pidx,)
        if not os.path.isfile('%s/%s.py' % (BASEDIR, name)):
            sys.stderr.write("autoplot/meta 404 %s\n" % (name, ))
            status = "404 Not Found"
            output = ""
            response_headers = [('Content-type', 'application/json'),
                                ('Content-Length', str(len(output)))]

            start_response(status, response_headers)

            return [output]
        try:
            timing = get_timing(pidx)
        except Exception as _:
            timing = -1
        fp, pathname, description = imp.find_module(name)
        app = imp.load_module(name, fp, pathname, description)
        data = app.get_description()
        data['timing[secs]'] = timing

        # Defaults
        data['arguments'].append(dict(type='text', name='dpi', default='100',
                                      label='Image Resolution (DPI)'))
    output = json.dumps(data)

    response_headers = [('Content-type', 'application/json'),
                        ('Content-Length', str(len(output)))]

    start_response(status, response_headers)

    return [output]
