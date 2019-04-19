"""Climodat Daily Data Estimator.

   python daily_estimator.py YYYY MM DD

RUN_NOON.sh - processes the current date, this skips any calendar day sites
RUN_NOON.sh - processes yesterday, running all sites
RUN_2AM.sh - processes yesterday, which should run all sites
"""
from __future__ import print_function
import sys
import datetime

import pandas as pd
from pandas.io.sql import read_sql
import numpy as np
from pyiem import iemre
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, ncopen
from pyiem.datatypes import temperature, distance
from pyiem.reference import TRACE_VALUE, state_names


def load_table(state, date):
    """Update the station table"""
    nt = NetworkTable("%sCLIMATE" % (state, ))
    rows = []
    istoday = (date == datetime.date.today())
    for sid in nt.sts:
        # handled by compute_0000
        if sid[2:] == '0000' or sid[2] == 'C':
            continue
        if istoday and not nt.sts[sid]['temp24_hour'] in range(3, 12):
            # print('skipping %s as is_today' % (sid, ))
            continue
        i, j = iemre.find_ij(nt.sts[sid]['lon'], nt.sts[sid]['lat'])
        nt.sts[sid]['gridi'] = i
        nt.sts[sid]['gridj'] = j
        rows.append(
            {'station': sid, 'gridi': i, 'gridj': j,
             'temp24_hour': nt.sts[sid]['temp24_hour'],
             'precip24_hour': nt.sts[sid]['precip24_hour'],
             'tracks': nt.sts[sid]['attributes'].get(
                 'TRACKS_STATION', '|').split("|")[0]}
        )
    if not rows:
        return
    df = pd.DataFrame(rows)
    df.set_index('station', inplace=True)
    for key in ['high', 'low', 'precip', 'snow', 'snowd']:
        df[key] = None
    return df


def estimate_precip(df, ts):
    """Estimate precipitation based on IEMRE"""
    idx = iemre.daily_offset(ts)
    nc = ncopen(iemre.get_daily_ncname(ts.year), 'r', timeout=300)
    grid12 = distance(nc.variables['p01d_12z'][idx, :, :],
                      'MM').value("IN").filled(0)
    grid00 = distance(nc.variables['p01d'][idx, :, :],
                      "MM").value("IN").filled(0)
    nc.close()

    for sid, row in df.iterrows():
        if not pd.isnull(row['precip']):
            continue
        if row['precip24_hour'] in [0, 22, 23]:
            precip = grid00[row['gridj'], row['gridi']]
        else:
            precip = grid12[row['gridj'], row['gridi']]
        # denote trace
        if precip > 0 and precip < 0.01:
            df.at[sid, 'precip'] = TRACE_VALUE
        elif precip < 0:
            df.at[sid, 'precip'] = 0
        elif np.isnan(precip) or np.ma.is_masked(precip):
            df.at[sid, 'precip'] = 0
        else:
            df.at[sid, 'precip'] = "%.2f" % (precip,)


def snowval(val):
    """Make sure our snow value makes database sense."""
    if val is None:
        return None
    return round(float(val), 1)


def estimate_snow(df, ts):
    """Estimate the Snow based on COOP reports"""
    idx = iemre.daily_offset(ts)
    nc = ncopen(iemre.get_daily_ncname(ts.year), 'r', timeout=300)
    snowgrid12 = distance(nc.variables['snow_12z'][idx, :, :],
                          'MM').value('IN').filled(0)
    snowdgrid12 = distance(nc.variables['snowd_12z'][idx, :, :],
                           'MM').value('IN').filled(0)
    nc.close()

    for sid, row in df.iterrows():
        if pd.isnull(row['snow']):
            df.at[sid, 'snow'] = snowgrid12[row['gridj'], row['gridi']]
        if pd.isnull(row['snowd']):
            df.at[sid, 'snowd'] = snowdgrid12[row['gridj'], row['gridi']]


def estimate_hilo(df, ts):
    """Estimate the High and Low Temperature based on gridded data"""
    idx = iemre.daily_offset(ts)
    nc = ncopen(iemre.get_daily_ncname(ts.year), 'r', timeout=300)
    highgrid12 = temperature(nc.variables['high_tmpk_12z'][idx, :, :],
                             'K').value('F')
    lowgrid12 = temperature(nc.variables['low_tmpk_12z'][idx, :, :],
                            'K').value('F')
    highgrid00 = temperature(nc.variables['high_tmpk'][idx, :, :],
                             'K').value('F')
    lowgrid00 = temperature(nc.variables['low_tmpk'][idx, :, :],
                            'K').value('F')
    nc.close()

    for sid, row in df.iterrows():
        if pd.isnull(row['high']):
            if row['temp24_hour'] in [0, 22, 23]:
                val = highgrid00[row['gridj'], row['gridi']]
            else:
                val = highgrid12[row['gridj'], row['gridi']]
            if sid == 'IA1402':
                print(row['temp24_hour'])
            if not np.ma.is_masked(val):
                df.at[sid, 'high'] = val
        if pd.isnull(row['low']):
            if row['temp24_hour'] in [0, 22, 23]:
                val = lowgrid00[row['gridj'], row['gridi']]
            else:
                val = lowgrid12[row['gridj'], row['gridi']]
            if not np.ma.is_masked(val):
                df.at[sid, 'low'] = val


def commit(cursor, table, df, ts):
    """
    Inject into the database!
    """
    # Inject!
    for sid, row in df.iterrows():
        if None in [row['high'], row['low'], row['precip']]:
            print(
                "daily_estimator cowardly refusing %s %s %s" % (sid, ts, row)
            )
            continue

        def do_update(_sid, _row):
            """inline."""
            sql = """
                UPDATE """ + table + """ SET high = %s, low = %s,
                precip = %s, snow = %s, snowd = %s, estimated = 't'
                WHERE day = %s and station = %s
                """
            args = (_row['high'], _row['low'],
                    _row['precip'], _row['snow'],
                    _row['snowd'], ts, _sid)
            cursor.execute(sql, args)
        do_update(sid, row)
        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO """ + table + """
            (station, day, sday, year, month)
            VALUES (%s, %s, %s, %s, %s)
            """, (sid, ts, ts.strftime("%m%d"), ts.year, ts.month))
            do_update(sid, row)


def merge_network_obs(df, network, ts):
    """Merge data from observations."""
    pgconn = get_dbconn('iem')
    obs = read_sql("""
        SELECT t.id as station,
        max_tmpf as high, min_tmpf as low, pday as precip, snow, snowd
        from summary s JOIN stations t
        on (t.iemid = s.iemid) WHERE t.network = %s and s.day = %s
    """, pgconn, params=(network, ts), index_col='station')
    df = df.join(obs, how='left', on='tracks', rsuffix='b')
    for col in ['high', 'low', 'precip', 'snow', 'snowd']:
        df[col].update(df[col+"b"])
        df.drop(col+"b", axis=1, inplace=True)
    return df


def main(argv):
    """main()"""
    date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    pgconn = get_dbconn('coop')
    for state in state_names:
        if state in ['AK', 'HI', 'DC']:
            continue
        table = "alldata_%s" % (state, )
        cursor = pgconn.cursor()
        df = load_table(state, date)
        df = merge_network_obs(df, "%s_COOP" % (state, ), date)
        df = merge_network_obs(df, "%s_ASOS" % (state, ), date)
        estimate_hilo(df, date)
        estimate_precip(df, date)
        estimate_snow(df, date)
        commit(cursor, table, df, date)
        cursor.close()
        pgconn.commit()


if __name__ == '__main__':
    # See how we are called
    main(sys.argv)
