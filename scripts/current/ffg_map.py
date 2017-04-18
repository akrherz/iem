"""Generate a Map showing current X hour FFG"""
import datetime
import sys

from pyiem.plot import MapPlot
import matplotlib.pyplot as plt
import psycopg2
from pandas.io.sql import read_sql


def main(argv):
    """Do FFG"""
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    df = read_sql("""
    WITH data as (
        SELECT ugc, rank() OVER (PARTITION by ugc ORDER by valid DESC), hour01
        from ffg WHERE valid > now() - '24 hours'::interval)
    SELECT *, substr(ugc, 3, 1) as ztype from data where rank = 1
    """, pgconn, index_col='ugc')
    m = MapPlot(sector='midwest', continentalcolor='white',
                title='NWS RFC 1 Hour Flash Flood Guidance on 7 PM 17 Apr 2017',
                subtitle='Estimated amount of One Hour Rainfall needed for non-urban Flash Flooding to commence')
    bins = [0.01, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.25, 2.5, 2.75, 3.,
            3.5, 4.0, 5.0]
    cmap = plt.get_cmap('gist_rainbow_r')
    df2 = df[df['ztype'] == 'C']
    m.fill_ugcs(df2['hour01'].to_dict(), bins, cmap=cmap, plotmissing=False)
    df2 = df[df['ztype'] == 'Z']
    m.fill_ugcs(df2['hour01'].to_dict(), bins, cmap=cmap, plotmissing=False,
                units='inches')
    m.postprocess(filename='test.png')
    m.close()


if __name__ == '__main__':
    main(sys.argv)
