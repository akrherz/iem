#!/usr/bin/env python
"""Returns the JSON metadata for a particular autoplot app, or all list all"""

import cgi
import sys
import os
import imp
import json
import psycopg2


def get_timing(pidx):
    """Return an average plot generation time for this app"""
    pgconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody',
                              timeout=5)
    cursor = pgconn.cursor()
    cursor.execute("""
        SELECT avg(timing) from autoplot_timing where appid = %s
        and valid > (now() - '7 days'::interval)
    """, (pidx, ))
    timing = cursor.fetchone()[0]
    return timing if timing is not None else -1


def main():
    """Do Something"""
    form = cgi.FieldStorage()
    pidx = int(form.getfirst('p', 0))

    if pidx == 0:
        import scripts  # @UnresolvedImport
        data = scripts.data
    else:
        if pidx >= 100:
            name = 'scripts100/p%s' % (pidx, )
        else:
            name = 'scripts/p%s' % (pidx,)
        if not os.path.isfile('%s.py' % (name, )):
            sys.stderr.write("autoplot/meta 404 %s" % (name, ))
            sys.stdout.write("Status: 404\n")
            sys.stdout.write("Content-type: text/plain\n\n")
            return
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
    sys.stdout.write("Content-type: application/json\n\n")
    sys.stdout.write(json.dumps(data))


if __name__ == '__main__':
    main()
