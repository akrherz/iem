#!/usr/bin/env python
"""
JSON webservice providing timestamps of available webcam images
"""
import cgi
import psycopg2
import json
import sys
import datetime
import pytz

dbconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
cursor = dbconn.cursor()


def dance(cid, start_ts, end_ts):
    """ Go get the dictionary of data we need and deserve """
    data = {'images': []}
    cursor.execute("""
        SELECT valid at time zone 'UTC', drct from camera_log where
        cam = %s and valid >= %s and valid < %s
    """, (cid, start_ts, end_ts))
    for row in cursor:
        uri = row[0].strftime(("http://mesonet.agron.iastate.edu/archive/"
                               "data/%Y/%m/%d/camera/" + cid + "/" +
                               cid + "_%Y%m%d%H%M.jpg"))
        data['images'].append(
            dict(valid=row[0].strftime("%Y-%m-%dT%H:%M:00Z"),
                 drct=row[1], href=uri))

    return data


def main():
    """ Do something, one time """
    form = cgi.FieldStorage()
    cid = form.getvalue("cid", 'KCCI-016')
    start_ts = form.getvalue('start_ts', None)
    end_ts = form.getvalue('end_ts', None)
    date = form.getvalue('date', None)
    if date is not None:
        start_ts = datetime.datetime.strptime(date, '%Y%m%d')
        start_ts = start_ts.replace(tzinfo=pytz.timezone("America/Chicago"))
        end_ts = start_ts + datetime.timedelta(days=1)
    else:
        start_ts = datetime.datetime.strptime(start_ts, '%Y%m%d%H%M')
        start_ts = start_ts.replace(tzinfo=pytz.timezone("UTC"))
        end_ts = datetime.datetime.strptime(end_ts, '%Y%m%d%H%M')
        end_ts = end_ts.replace(tzinfo=pytz.timezone("UTC"))

    sys.stdout.write("Content-type: application/json\n\n")
    sys.stdout.write(json.dumps(dance(cid, start_ts, end_ts)))

if __name__ == '__main__':
    main()
