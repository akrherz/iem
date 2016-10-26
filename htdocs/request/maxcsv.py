#!/usr/bin/env python
"""Provide some CSV Files

first four columns need to be
ID,Station,Latitude,Longitude
"""
import cgi
import datetime
import sys
import psycopg2
from pandas.io.sql import read_sql

SSW = sys.stdout.write
#>> *         DOT plows
#>> *         RWIS sensor data
#>> *         River gauges
#>> *         Ag data (4" soil temps)


def do_iaroadcond():
    """Iowa DOT Road Conditions as dots"""
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    df = read_sql("""
    select b.idot_id as locationid,
    replace(b.longname, ',', ' ') as locationname,
    ST_y(ST_transform(ST_centroid(b.geom),4326)) as latitude,
    ST_x(ST_transform(ST_centroid(b.geom),4326)) as longitude, cond_code
    from roads_base b JOIN roads_current c on (c.segid = b.segid)
    """, pgconn)
    return df


def do_webcams(network):
    """direction arrows"""
    pgconn = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
    df = read_sql("""
    select cam as locationid, w.name as locationname, st_y(geom) as latitude,
    st_x(geom) as longitude, drct
    from camera_current c JOIN webcams w on (c.cam = w.id)
    WHERE c.valid > (now() - '30 minutes'::interval) and w.network = %s
    """, pgconn, params=(network,))
    return df


def do_iowa_azos(date):
    """Dump high and lows for Iowa ASOS + AWOS """
    table = "summary_%s" % (date.year,)
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    df = read_sql("""
    select id as locationid, n.name as locationname, st_y(geom) as latitude,
    st_x(geom) as longitude, s.day, s.max_tmpf::int as high,
    s.min_tmpf::int as low, pday as precip
    from stations n JOIN """ + table + """ s on (n.iemid = s.iemid)
    WHERE n.network in ('IA_ASOS', 'AWOS') and s.day = %s
    """, pgconn, params=(date,))
    return df


def do_ahps(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = psycopg2.connect(database='hads', host='iemdb-hads',
                              user='nobody')
    cursor = pgconn.cursor()
    # Get metadata
    cursor.execute("""
        SELECT name, st_x(geom), st_y(geom) from stations
        where id = %s and network ~* 'DCP'
    """, (nwsli,))
    row = cursor.fetchone()
    latitude = row[2]
    longitude = row[1]
    stationname = row[0]
    # Get the last forecast
    cursor.execute("""
        select id, forecast_sts at time zone 'UTC',
        generationtime at time zone 'UTC', primaryname, primaryunits,
        secondaryname, secondaryunits
        from hml_forecast where station = %s
        and generationtime > now() - '7 days'::interval
        ORDER by issued DESC LIMIT 1
    """, (nwsli,))
    row = cursor.fetchone()
    primaryname = row[3]
    generationtime = row[2]
    primaryunits = row[4]
    secondaryname = row[5]
    secondaryunits = row[6]
    y = "{}".format(generationtime.year)
    # Get the latest forecast
    fdf = read_sql("""
    SELECT valid, primary_value, secondary_value, 'F' as type from
    hml_forecast_data_"""+y+""" WHERE hml_forecast_id = %s
    ORDER by valid ASC
    """, pgconn, params=(row[0],), index_col=None)
    # Get the obs
    plabel = "{}[{}]".format(primaryname, primaryunits)
    slabel = "{}[{}]".format(secondaryname, secondaryunits)
    odf = read_sql("""
    WITH primaryv as (
      SELECT valid, value from hml_observed_data WHERE station = %s
      and key = get_hml_observed_key(%s) and valid > now() - '1 day'::interval
    ), secondaryv as (
      SELECT valid, value from hml_observed_data WHERE station = %s
      and key = get_hml_observed_key(%s) and valid > now() - '1 day'::interval
    )
    SELECT p.valid, p.value as primary_value, s.value as secondary_value,
    'O' as type
    from primaryv p LEFT JOIN secondaryv s ON (p.valid = s.valid)
    ORDER by p.valid DESC
    """, pgconn, params=(nwsli, plabel, nwsli, slabel),
                   index_col=None)
    sys.stderr.write(str(primaryname))
    sys.stderr.write(str(secondaryname))
    df = fdf.append(odf)
    df['locationid'] = nwsli
    df['locationname'] = stationname
    df['latitude'] = latitude
    df['longitude'] = longitude
    df['Time'] = df['valid'].dt.strftime("%m/%d/%Y %H:%M")
    df[plabel] = df['primary_value']
    df[slabel] = df['secondary_value']
    # we have to do the writing from here
    SSW("Content-type: text/plain\n\n")
    SSW("Observed Data:,,\n")
    SSW("|Date(UTC)|,|Stage|,|--Flow-|\n")
    odf = df[df['type'] == 'O']
    row = odf.iloc[0]
    SSW("%s,%.2fft,%.1fkcfs\n" % (row['Time'], row['Stage[ft]'],
                                  row['Flow[kcfs]']))
    SSW("Forecast Data (Issued %s UTC):,\n" % (
        generationtime.strftime("%m-%d-%Y %H:%M:%S"),))
    SSW("|Date(UTC)|,|Stage|,|--Flow-|\n")
    odf = df[df['type'] == 'F']
    for _, row in odf.iterrows():
        SSW("%s,%.2fft,%.1fkcfs\n" % (row['Time'], row['Stage[ft]'],
                                      row['Flow[kcfs]']))

    sys.exit(0)


def router(q):
    """Process and return dataframe"""
    if q.startswith("ahps_"):
        do_ahps(q[5:].upper())  # we write ourselves and exit
    elif q == 'iaroadcond':
        df = do_iaroadcond()
    elif q == 'iadotplows':
        df = do_iadotplows()
    elif q == 'iarwis':
        df = do_iariws()
    elif q == 'iariver':
        df = do_iariver()
    elif q == 'isusm':
        df = do_isusm()
    elif q == 'iowayesterday':
        df = do_iowa_azos(datetime.date.today() - datetime.timedelta(days=1))
    elif q == 'iowatoday':
        df = do_iowa_azos(datetime.date.today())
    elif q == 'kcrgcitycam':
        df = do_webcams('KCRG')
    else:
        sys.stdout.write("""ERROR, unknown report specified""")
        sys.exit()
    return df


def main():
    """Do Something"""
    form = cgi.FieldStorage()
    q = form.getfirst('q')
    df = router(q)
    SSW("Content-type: text/plain\n\n")
    SSW(df.to_csv(None, index=False))
    SSW("\n")

if __name__ == '__main__':
    main()
