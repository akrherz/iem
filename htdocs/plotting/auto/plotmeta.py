#!/usr/bin/env python

import cgi
import sys
import os
import imp
import json


def main():
    form = cgi.FieldStorage()
    p = int(form.getfirst('p', 0))

    if p == 0:
        import scripts  # @UnresolvedImport
        data = scripts.data
    else:
        if p >= 100:
            name = 'scripts100/p%s' % (p, )
        else:
            name = 'scripts/p%s' % (p,)
        if not os.path.isfile('%s.py' % (name, )):
            sys.stderr.write("autoplot/meta 404 %s" % (name, ))
            sys.stdout.write("Status: 404\n")
            sys.stdout.write("Content-type: text/plain\n\n")
            return
        fp, pathname, description = imp.find_module(name)
        a = imp.load_module(name, fp, pathname, description)
        data = a.get_description()

        # Defaults
        data['arguments'].append(dict(type='text', name='dpi', default='100',
                                      label='Image Resolution (DPI)'))
    sys.stdout.write("Content-type: application/json\n\n")
    sys.stdout.write(json.dumps(data))


if __name__ == '__main__':
    main()
