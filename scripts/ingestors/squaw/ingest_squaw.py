"""Process the Flow data provided by the USGS website"""
from __future__ import print_function
import re
import urllib2

from pyiem.util import get_dbconn


def main():
    """Squaw"""
    mydb = get_dbconn("squaw")
    cursor = mydb.cursor()

    uri = ("http://waterdata.usgs.gov/ia/nwis/uv?dd_cd=01&format=rdb&"
           "period=2&site_no=05470500")

    data = urllib2.urlopen(uri, timeout=30).read()

    tokens = re.findall(
        "USGS\t([0-9]*)\t(....-..-.. ..:..)\t([CSDT]+)\t([0-9]*)", data)

    for ob in tokens:
        sql = "SELECT * from real_flow WHERE valid = '%s'" % (ob[1], )
        cursor.execute(sql)
        if cursor.rowcount > 0:
            continue
        if ob[3] != '':
            sql = """
                INSERT into real_flow(gauge_id, valid, cfs)
                VALUES (%s, '%s', %s)
            """ % (ob[0], ob[1], ob[3])
            cursor.execute(sql)

    cursor.close()
    mydb.commit()
    mydb.close()


if __name__ == '__main__':
    main()
