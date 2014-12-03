#!/usr/bin/env python
"""
Return JSON metadata for GOES Imagery
"""
import sys
import cgi
import json
import os
import glob
import datetime

BIRDS = ['EAST', 'WEST']
PRODUCTS = ['WV', 'VIS', 'IR']

def parse_time(s):
    """
    Convert ISO something into a mx.DateTime
    """
    try:
        if len(s) == 17:
            date = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%MZ')
        elif len(s) == 20:
            date = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
        else:
            date = datetime.datetime.utcnow()
    except:
        date = datetime.datetime.utcnow()
    return date

def find_scans(root, bird, product, start_gts, end_gts):
    """ Find GOES SCANs """
    if bird not in BIRDS or product not in PRODUCTS:
        return
    now = start_gts.replace(hour=0,minute=0,second=0)
    while now < end_gts:
        mydir = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/sat/awips211")
        sys.stderr.write(mydir)
        if os.path.isdir(mydir):
            os.chdir(mydir)
            files = glob.glob("GOES_%s_%s_*.wld" % (bird, product))
            files.sort()
            for f in files:
                ts = datetime.datetime.strptime(f[:-4].split("_")[3],
                                                "%Y%m%d%H%M")
                root['scans'].append(ts.strftime("%Y-%m-%dT%H:%M:00Z"))
        now += datetime.timedelta(hours=24)

def list_files(form):
    """
    List available GOES files based on the form request
    """
    bird = form.getvalue('bird', 'EAST').upper()
    product = form.getvalue('product', 'VIS').upper()
    start_gts = parse_time( form.getvalue('start', '2012-01-27T00:00Z') )
    end_gts = parse_time( form.getvalue('end', '2012-01-27T01:00Z') )
    root = {'scans': []}
    find_scans(root, bird, product, start_gts, end_gts)
        
    return root

def main():
    """
    
    """
    form = cgi.FieldStorage()
    operation = form.getvalue('operation', None)
    callback = form.getvalue('callback', None)
    if callback is not None:
        sys.stdout.write("Content-type: application/javascript\n\n")
        sys.stdout.write("%s(" % (callback,))
    else:
        sys.stdout.write("Content-type: text/plain\n\n")
    if operation == "list":
        sys.stdout.write(json.dumps( list_files(form) ))
    if callback is not None:
        sys.stdout.write(')')

if __name__ == "__main__":
    main()
#END