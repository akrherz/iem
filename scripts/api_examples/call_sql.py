"""Example script showing IEM SQL API

"""
from __future__ import print_function
import urllib2
import urllib
import json


def main():
    """Go Main Go"""
    threshold = 1.0  # inches

    data = {'sql': """
    WITH data as (
     SELECT station, min(year) as minyr, count(*) as years,
     avg(sum) as days from
     (SELECT station, year, sum(case when precip >= %s THEN 1 else 0 end)
     from alldata_ia GROUP by station, year) as foo GROUP by station
    )

     SELECT ST_x(t.geom), ST_y(t.geom), station, minyr, years, days
     from data d JOIN stations t on (t.id = d.station)
     WHERE t.network = 'IACLIMATE'

    """ % (threshold,)}

    url = 'https://mesonet.agron.iastate.edu/api/sql/database/coop'
    url = '%s?%s' % (url, urllib.urlencode(data))

    data = json.load(urllib2.urlopen(url))

    print('LON,LAT,START_YEAR,COUNT_YEARS,DAYS_PER_YEAR')

    for row in data['results']:
        print(('%.2f,%.2f,%s,%s,%.2f'
               ) % (row['st_x'], row['st_y'], row['minyr'],
                    row["years"], row['days']))


if __name__ == '__main__':
    main()
