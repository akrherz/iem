#!/usr/bin/env python
"""
 Download interface for ISU-SM data
"""
import cgi
import datetime
import psycopg2.extras
import sys
import pandas as pd
import cStringIO
from pyiem.datatypes import temperature
ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
cursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)


def get_stations(form):
    ''' Figure out which stations were requested '''
    stations = form.getlist('sts')
    if len(stations) == 0:
        stations.append('XXXXX')
    if len(stations) == 1:
        stations.append('XXXXX')
    return stations


def get_dates(form):
    ''' Get the start and end dates requested '''
    year1 = form.getfirst('year1', 2013)
    month1 = form.getfirst('month1', 1)
    day1 = form.getfirst('day1', 1)
    year2 = form.getfirst('year2', 2013)
    month2 = form.getfirst('month2', 1)
    day2 = form.getfirst('day2', 1)

    try:
        sts = datetime.datetime(int(year1), int(month1), int(day1))
        ets = datetime.datetime(int(year2), int(month2), int(day2))
    except:
        sys.stdout.write("Content-type: text/plain\n\n")
        sys.stdout.write(("ERROR: Failed to parse specified start and end "
                          "dates.  Please go back and ensure that you have "
                          "specified valid dates.  For example, 31 November "
                          "does not exist."))
        sys.exit()

    if sts > ets:
        sts2 = ets
        ets = sts
        sts = sts2
    if sts == ets:
        ets = sts + datetime.timedelta(days=1)
    return sts, ets


def get_delimiter(form):
    ''' Figure out what is the requested delimiter '''
    d = form.getvalue('delim', 'comma')
    if d == 'comma':
        return ','
    return '\t'


def fetch_daily(form, cols):
    ''' Return a fetching of daily data '''
    sts, ets = get_dates(form)
    stations = get_stations(form)
    delim = get_delimiter(form)
    if delim == 'tab':
        delim = '\t'
    elif delim == 'comma':
        delim = ','
    elif delim == 'space':
        delim = ' '

    if len(cols) == 0:
        cols = ["station", "valid", "high", "low", "gdd50", "solar", "precip",
                "sped", "gust", "et", "soil04t", "soil12t", "soil24t",
                "soil50t", "soil12vwc", "soil24vwc", "soil50vwc"]
    else:
        cols.insert(0, 'valid')
        cols.insert(0, 'station')

    sql = """
    --- Get the Daily Max/Min soil values
    WITH soils as (
      SELECT station, date(valid) as date,
      min(tsoil_c_avg) as soil04tn, max(tsoil_c_avg) as soil04tx,
      min(t12_c_avg) as soil12tn, max(t12_c_avg) as soil12tx,
      min(t24_c_avg) as soil24tn, max(t24_c_avg) as soil24tx,
      min(t50_c_avg) as soil50tn, max(t50_c_avg) as soil50tx
      from sm_hourly where
      valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
      GROUP by station, date
    ), daily as (
      SELECT station, valid, tair_c_max, tair_c_min, slrmj_tot,
      rain_mm_tot, dailyet, tsoil_c_avg, t12_c_avg, t24_c_avg, t50_c_avg,
      vwc_12_avg, vwc_24_avg, vwc_50_avg, ws_mps_s_wvt, ws_mps_max
      from sm_daily WHERE
      valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    )
    SELECT d.station, d.valid, s.date, s.soil04tn, s.soil04tx,
    s.soil12tn, s.soil12tx, s.soil24tn, s.soil24tx,
    s.soil50tn, s.soil50tx, tair_c_max, tair_c_min, slrmj_tot,
    rain_mm_tot, dailyet, tsoil_c_avg, t12_c_avg, t24_c_avg, t50_c_avg,
    vwc_12_avg, vwc_24_avg, vwc_50_avg, ws_mps_s_wvt, ws_mps_max,
    round(gddxx(50, 86, c2f( tair_c_max ),
    c2f( tair_c_min ))::numeric,1) as gdd50
    FROM soils s JOIN daily d on (d.station = s.station and s.date = d.valid)
    ORDER by d.valid ASC
    """ % (
      sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"), str(tuple(stations)),
      sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"), str(tuple(stations))
      )
    cursor.execute(sql)

    values = []

    for row in cursor:
        valid = row['valid']
        station = row['station']
        high = temperature(row['tair_c_max'],
                           'C').value(
            'F') if row['tair_c_max'] is not None else -99
        low = temperature(row['tair_c_min'],
                          'C').value(
            'F') if row['tair_c_min'] is not None else -99
        precip = row['rain_mm_tot'] / 24.5 if row['rain_mm_tot'] > 0 else 0
        et = row['dailyet'] / 24.5 if row['dailyet'] > 0 else 0

        soil04t = temperature(row['tsoil_c_avg'],
                              'C').value(
            'F') if row['tsoil_c_avg'] is not None else -99
        soil04tn = temperature(row['soil04tn'],
                               'C').value(
            'F') if row['soil04tn'] is not None else -99
        soil04tx = temperature(row['soil04tx'],
                               'C').value(
            'F') if row['soil04tx'] is not None else -99

        soil12t = temperature(row['t12_c_avg'],
                              'C').value(
            'F') if row['t12_c_avg'] is not None else -99
        soil12tn = temperature(row['soil12tn'],
                               'C').value(
            'F') if row['soil12tn'] is not None else -99
        soil12tx = temperature(row['soil12tx'],
                               'C').value(
            'F') if row['soil12tx'] is not None else -99

        soil24t = temperature(row['t24_c_avg'],
                              'C').value(
            'F') if row['t24_c_avg'] is not None else -99
        soil24tn = temperature(row['soil24tn'],
                               'C').value(
            'F') if row['soil24tn'] is not None else -99
        soil24tx = temperature(row['soil24tx'],
                               'C').value(
            'F') if row['soil24tx'] is not None else -99

        soil50t = temperature(row['t50_c_avg'],
                              'C').value(
            'F') if row['t50_c_avg'] is not None else -99
        soil50tn = temperature(row['soil50tn'],
                               'C').value(
            'F') if row['soil50tn'] is not None else -99
        soil50tx = temperature(row['soil50tx'],
                               'C').value(
            'F') if row['soil50tx'] is not None else -99

        soil12vwc = row['vwc_12_avg'] if row['vwc_12_avg'] is not None else -99
        soil24vwc = row['vwc_24_avg'] if row['vwc_24_avg'] is not None else -99
        soil50vwc = row['vwc_50_avg'] if row['vwc_50_avg'] is not None else -99
        speed = (row['ws_mps_s_wvt'] * 2.23 if row['ws_mps_s_wvt'] is not None
                 else -99)
        gust = (row['ws_mps_max'] * 2.23 if row['ws_mps_max'] is not None
                else -99)

        values.append(dict(station=station, valid=valid.strftime("%Y-%m-%d"),
                           high=high, low=low, solar=row['slrmj_tot'],
                           gdd50=row['gdd50'], precip=precip, sped=speed,
                           gust=gust, et=et, soil04t=soil04t, soil12t=soil12t,
                           soil24t=soil24t, soil50t=soil50t,
                           soil04tn=soil04tn, soil04tx=soil04tx,
                           soil12tn=soil12tn, soil12tx=soil12tx,
                           soil24tn=soil24tn, soil24tx=soil24tx,
                           soil50tn=soil50tn, soil50tx=soil50tx,
                           soil12vwc=soil12vwc, soil24vwc=soil24vwc,
                           soil50vwc=soil50vwc))

    if len(values) == 0:
        return 'Sorry, no data found for this query.'

    df = pd.DataFrame(values)
    buf = cStringIO.StringIO()
    df.to_csv(buf, index=False, columns=cols, sep=delim, float_format='%7.2f')
    buf.seek(0)
    return buf.read()


def fetch_hourly(form, cols):
    ''' Return a fetching of hourly data '''
    sts, ets = get_dates(form)
    stations = get_stations(form)
    delim = get_delimiter(form)
    if delim == 'tab':
        delim = '\t'
    elif delim == 'comma':
        delim = ','
    elif delim == 'space':
        delim = ' '

    if len(cols) == 0:
        cols = ["station", "valid", "tmpf", "relh", "solar", "precip",
                "speed", "drct", "et", "soil04t", "soil12t", "soil24t",
                "soil50t",
                "soil12vwc", "soil24vwc", "soil50vwc"]
    else:
        cols.insert(0, 'valid')
        cols.insert(0, 'station')

    cursor.execute("""SELECT station, valid, tair_c_avg, rh, slrkw_avg,
    rain_mm_tot, ws_mps_s_wvt, winddir_d1_wvt, etalfalfa, tsoil_c_avg,
    t12_c_avg, t24_c_avg, t50_c_avg, vwc_12_avg, vwc_24_avg, vwc_50_avg
    from sm_hourly
    WHERE valid >= '%s 00:00' and valid < '%s 00:00' and station in %s
    ORDER by valid ASC
    """ % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"),
           str(tuple(stations))))

    values = []

    for row in cursor:
        valid = row['valid']
        station = row['station']
        tmpf = temperature(row['tair_c_avg'],
                           'C').value(
            'F') if row['tair_c_avg'] is not None else -99
        relh = row['rh'] if row['rh'] is not None else -99
        solar = row['slrkw_avg'] if row['slrkw_avg'] is not None else -99
        precip = (row['rain_mm_tot'] / 24.5 if row['rain_mm_tot'] is not None
                  else -99)
        speed = (row['ws_mps_s_wvt'] * 2.23 if row['ws_mps_s_wvt'] is not None
                 else -99)
        drct = (row['winddir_d1_wvt'] if row['winddir_d1_wvt'] is not None
                else -99)
        et = row['etalfalfa'] / 24.5 if row['etalfalfa'] is not None else -99
        soil04t = temperature(row['tsoil_c_avg'],
                              'C').value(
            'F') if row['tsoil_c_avg'] is not None else -99
        soil12t = temperature(row['t12_c_avg'],
                              'C').value(
            'F') if row['t12_c_avg'] is not None else -99
        soil24t = temperature(row['t24_c_avg'],
                              'C').value(
            'F') if row['t24_c_avg'] is not None else -99
        soil50t = temperature(row['t50_c_avg'],
                              'C').value(
            'F') if row['t50_c_avg'] is not None else -99
        soil12vwc = row['vwc_12_avg'] if row['vwc_12_avg'] is not None else -99
        soil24vwc = row['vwc_24_avg'] if row['vwc_24_avg'] is not None else -99
        soil50vwc = row['vwc_50_avg'] if row['vwc_50_avg'] is not None else -99

        values.append(dict(station=station,
                           valid=valid.strftime("%Y-%m-%d %H:%M"),
                           tmpf=tmpf, relh=relh, solar=solar, precip=precip,
                           speed=speed, drct=drct, et=et,  soil04t=soil04t,
                           soil12t=soil12t, soil24t=soil24t, soil50t=soil50t,
                           soil12vwc=soil12vwc, soil24vwc=soil24vwc,
                           soil50vwc=soil50vwc))

    if len(values) == 0:
        return 'Sorry, no data found for this query.'

    df = pd.DataFrame(values)
    buf = cStringIO.StringIO()
    df.to_csv(buf, index=False, columns=cols, sep=delim, float_format='%7.2f')
    buf.seek(0)
    return buf.read()


def main(argv):
    """Do things"""
    form = cgi.FieldStorage()
    mode = form.getfirst('mode', 'hourly')
    cols = form.getlist('vars')
    if mode == 'hourly':
        res = fetch_hourly(form, cols)
    else:
        res = fetch_daily(form, cols)

    todisk = form.getfirst('todisk', 'no')
    if todisk == 'yes':
        sys.stdout.write("Content-type: text/plain\n")
        sys.stdout.write(("Content-Disposition: attachment; "
                          "filename=isusm.txt\n\n"))
    else:
        sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(res)

if __name__ == '__main__':
    ''' make stuff happen '''
    main(sys.argv)
