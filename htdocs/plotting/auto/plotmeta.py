#!/usr/bin/env python

import cgi
import sys
import imp
import json


if __name__ == '__main__':
    form = cgi.FieldStorage()
    p = int(form.getfirst('p', 0))

    if p == 0:
        import scripts
        data = scripts.data
    else:
        if p >= 100:
            name = 'scripts100/p%s' % (p, )
        else:
            name = 'scripts/p%s' % (p,)
        fp, pathname, description = imp.find_module(name)
        a = imp.load_module(name, fp, pathname, description)
        data = a.get_description()

        # Defaults
        data['arguments'].append(dict(type='text', name='dpi', default='100',
                                      label='Image Resolution (DPI)'))
    sys.stdout.write("Content-type: application/json\n\n")
    sys.stdout.write(json.dumps(data))
