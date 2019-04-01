#!/usr/bin/env python
"""
Return JSON metadata for nexrad information
"""
import cgi
import json
import datetime
import os.path
import glob

from pyiem.util import get_dbconn, ssw
NIDS = {
    'N0Q': 'Base Reflectivity (High Res)',
    'N0U': 'Base Radial Velocity (High Res)',
    'N0S': 'Storm Relative Radial Velocity',
    'NET': 'Echo Tops',
    'N0R': 'Base Reflectivity',
    'N0V': 'Base Radial Velocity',
    'N0Z': 'Base Reflectivity',
    'TR0': 'TDWR Base Reflectivity',
    'TV0': 'TDWR Radial Velocity',
}


def parse_time(s):
    """
    Convert ISO something into a datetime
    """
    try:
        if len(s) == 17:
            date = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%MZ')
        elif len(s) == 20:
            date = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
        else:
            date = datetime.datetime.utcnow()
    except Exception as _exp:
        date = datetime.datetime.utcnow()
    return date


def available_radars(form):
    """
    Return available RADAR sites for the given location and date!
    """
    lat = form.getvalue('lat', None)
    lon = form.getvalue('lon', None)
    start_gts = parse_time(form.getvalue('start', '2012-01-27T00:00Z'))
    pgconn = get_dbconn('mesosite')
    mcursor = pgconn.cursor()
    root = {'radars': []}
    if lat is None or lon is None:
        sql = """
        select id, name,
        ST_x(geom) as lon, ST_y(geom) as lat, network
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        ORDER by id asc"""
    else:
        sql = """
        select id, name, ST_x(geom) as lon, ST_y(geom) as lat, network,
        ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT(%s %s)')) as dist
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        and ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT(%s %s)')) < 3
        ORDER by dist asc
        """ % (lon, lat, lon, lat)
    mcursor.execute(sql)
    root['radars'].append({'id': 'USCOMP', 'name': 'National Composite',
                           'lat': 42.5, 'lon': -95, 'type': 'COMPOSITE'})
    for row in mcursor:
        radar = row[0]
        if not os.path.isdir(start_gts.strftime(("/mesonet/ARCHIVE/data/"
                                                 "%Y/%m/%d/GIS/ridge/" +
                                                 radar))):
            continue
        root['radars'].append({'id': radar, 'name': row[1], 'lat': row[3],
                               'lon': row[2], 'type': row[4]})
    mcursor.close()
    pgconn.close()
    return root


def find_scans(root, radar, product, sts, ets):
    """Find scan times with data

    Note that we currently have a 500 length hard coded limit, so if we are
    interested in a long term time period, we should lengthen out our
    interval to look for files

    Args:
      root (dict): where we write our findings to
      radar (string): radar we are interested in
      product (string): NEXRAD product of interest
      sts (datetime): start time to look for data
      ets (datetime): end time to look for data
    """
    now = sts
    times = []
    if radar in ['USCOMP', ]:
        # These are every 5 minutes, so 288 per day
        now -= datetime.timedelta(minutes=(now.minute % 5))
        while now < ets:
            if os.path.isfile(now.strftime(("/mesonet/ARCHIVE/data/"
                                            "%Y/%m/%d/GIS/uscomp/" +
                                            product.lower() +
                                            "_%Y%m%d%H%M.png"))):
                times.append({'ts': now.strftime("%Y-%m-%dT%H:%MZ")})
            now += datetime.timedelta(minutes=5)
    else:
        while now < ets:
            if os.path.isfile(now.strftime("/mesonet/ARCHIVE/data/"
                                           "%Y/%m/%d/GIS/ridge/" +
                                           radar + "/" + product +
                                           "/" + radar + "_" +
                                           product + "_%Y%m%d%H%M.png")):
                times.append({'ts': now.strftime("%Y-%m-%dT%H:%MZ")})
            now += datetime.timedelta(minutes=1)
    if len(times) > 500:
        # Do some filtering
        interval = int((len(times) / 500) + 1)
        times = times[::interval]

    root['scans'] = times


def is_realtime(sts):
    """
    Check to see if this time is close to realtime...
    """
    if (datetime.datetime.utcnow() - sts).total_seconds() > 3600:
        return False
    return True


def list_files(form):
    """
    List available NEXRAD files based on the form request
    """
    radar = form.getvalue('radar', 'DMX')[:10]
    product = form.getvalue('product', 'N0Q')[:3]
    start_gts = parse_time(form.getvalue('start', '2012-01-27T00:00Z'))
    end_gts = parse_time(form.getvalue('end', '2012-01-27T01:00Z'))
    # practical limit here of 10 days
    if (start_gts + datetime.timedelta(days=10)) < end_gts:
        end_gts = start_gts + datetime.timedelta(days=10)
    root = {'scans': []}
    find_scans(root, radar, product, start_gts, end_gts)
    if not root['scans'] and is_realtime(start_gts):
        now = start_gts - datetime.timedelta(minutes=10)
        find_scans(root, radar, product, now, end_gts)

    return root


def list_products(form):
    """
    List available NEXRAD products
    """
    radar = form.getvalue('radar', 'DMX')[:10]
    now = parse_time(form.getvalue('start', '2012-01-27T00:00Z'))
    root = {'products': []}
    if radar == 'USCOMP':
        for dirname in ['N0Q', 'N0R']:
            testfp = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"
                                   "uscomp/" + dirname.lower() +
                                   "_%Y%m%d0000.png"))
            if os.path.isfile(testfp):
                root['products'].append({'id': dirname,
                                         'name': NIDS.get(dirname, dirname)})
    else:
        basedir = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/" +
                                radar))
        if os.path.isdir(basedir):
            os.chdir(basedir)
            for dirname in glob.glob("???"):
                root['products'].append({'id': dirname,
                                         'name': NIDS.get(dirname, dirname)})
    return root


def main():
    """Do awesome things"""
    form = cgi.FieldStorage()
    if os.environ['REQUEST_METHOD'] not in ['GET', 'POST']:
        ssw("Content-type: text/plain\n\n")
        ssw("HTTP METHOD NOT ALLOWED")
        return
    operation = form.getvalue('operation', None)
    callback = form.getvalue('callback', None)
    if callback is not None:
        ssw("Content-type: application/javascript\n\n")
        ssw("%s(" % (cgi.escape(callback, quote=True),))
    else:
        ssw("Content-type: text/plain\n\n")
    if operation == "list":
        ssw(json.dumps(list_files(form)))
    elif operation == "available":
        ssw(json.dumps(available_radars(form)))
    elif operation == "products":
        ssw(json.dumps(list_products(form)))
    if callback is not None:
        ssw(')')


if __name__ == "__main__":
    main()
