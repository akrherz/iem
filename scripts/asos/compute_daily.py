"""Compute daily summaries of ASOS/METAR data

Called from RUN_12Z.sh for the previous date
"""
from __future__ import print_function
import sys
import datetime
import warnings

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import metpy.calc as mcalc
from metpy.units import units as munits
from pyiem.util import get_dbconn

# bad values into mcalc
warnings.simplefilter("ignore", RuntimeWarning)


def clean(val, floor, ceiling):
    """Make sure RH values are always sane"""
    if val > ceiling or val < floor or pd.isna(val):
        return None
    if isinstance(val, munits.Quantity):
        return float(val.magnitude)
    return float(val)


def do(ts):
    """Process this date timestamp"""
    asos = get_dbconn('asos', user='nobody')
    iemaccess = get_dbconn('iem')
    icursor = iemaccess.cursor()
    df = read_sql("""
    select station, network, iemid, drct, sknt,
    valid at time zone tzname as localvalid,
    tmpf, dwpf, relh, feel from
    alldata d JOIN stations t on (t.id = d.station)
    where (network ~* 'ASOS' or network = 'AWOS')
    and valid between %s and %s and t.tzname is not null
    and date(valid at time zone tzname) = %s
    ORDER by valid ASC
    """, asos, params=(ts - datetime.timedelta(days=2),
                       ts + datetime.timedelta(days=2),
                       ts.strftime("%Y-%m-%d")), index_col=None)
    if df.empty:
        print("compute_daily no ASOS database entries for %s" % (ts, ))
        return
    # derive some parameters
    df['u'], df['v'] = mcalc.wind_components(
        df['sknt'].values * munits.knots,
        df['drct'].values * munits.deg
    )
    df['localvalid_lag'] = df.groupby('iemid')['localvalid'].shift(1)
    df['timedelta'] = df['localvalid'] - df['localvalid_lag']
    ndf = df[pd.isna(df['timedelta'])]
    df.loc[ndf.index.values, 'timedelta'] = pd.to_timedelta(
            ndf['localvalid'].dt.hour * 3600. +
            ndf['localvalid'].dt.minute * 60., unit='s'
    )
    df['timedelta'] = df['timedelta'] / np.timedelta64(1, 's')

    table = "summary_%s" % (ts.year,)
    for iemid, gdf in df.groupby('iemid'):
        if len(gdf.index) < 6:
            # print(" Quorum not meet for %s" % (gdf.iloc[0]['station'], ))
            continue
        ldf = gdf.copy()
        ldf.interpolate(inplace=True)
        totsecs = ldf['timedelta'].sum()
        avg_rh = clean((ldf['relh'] * ldf['timedelta']).sum() / totsecs, 1,
                       100)
        min_rh = clean(ldf['relh'].min(), 1, 100)
        max_rh = clean(ldf['relh'].max(), 1, 100)

        uavg = (ldf['u'] * ldf['timedelta']).sum() / totsecs
        vavg = (ldf['v'] * ldf['timedelta']).sum() / totsecs
        drct = clean(
            mcalc.wind_direction(uavg * munits.knots, vavg * munits.knots),
            0, 360)
        avg_sknt = clean(
            (ldf['sknt'] * ldf['timedelta']).sum() / totsecs, 0, 150  # arb
        )
        max_feel = clean(ldf['feel'].max(), -150, 200)
        avg_feel = clean(
            (ldf['feel'] * ldf['timedelta']).sum() / totsecs, -150, 200
        )
        min_feel = clean(ldf['feel'].min(), -150, 200)

        def do_update():
            """Inline updating"""
            icursor.execute("""
            UPDATE """ + table + """
            SET avg_rh = %s, min_rh = %s, max_rh = %s,
            avg_sknt = %s, vector_avg_drct = %s,
            min_feel = %s, avg_feel = %s, max_feel = %s
            WHERE
            iemid = %s and day = %s
            """, (avg_rh, min_rh, max_rh, avg_sknt, drct,
                  min_feel, avg_feel, max_feel,
                  iemid, ts))
        do_update()
        if icursor.rowcount == 0:
            print(('compute_daily Adding %s for %s %s %s'
                   ) % (table, gdf.iloc[0]['station'], gdf.iloc[0]['network'],
                        ts))
            icursor.execute("""
                INSERT into """ + table + """
                (iemid, day) values (%s, %s)
            """, (iemid, ts))
            do_update()

    icursor.close()
    iemaccess.commit()
    iemaccess.close()


def main(argv):
    """Go Main Go"""
    ts = datetime.date.today() - datetime.timedelta(days=1)
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    do(ts)


if __name__ == '__main__':
    main(sys.argv)
