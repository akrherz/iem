"""Climodat Daily Data Estimator

TASK: Given that it takes the QC'd data many months to make the round trip,
      we need to generate estimates so that the climodat reports are more
      useful even if the estimated data has problems

Columns to complete:

 stationid | character(6)     | OK
 day       | date             | OK
 high      | integer          | COOP obs
 low       | integer          | COOP obs
 precip    | double precision | COOP precip
 snow      | double precision | COOP snow
 sday      | character(4)     | OK
 year      | integer          | OK
 month     | smallint         | OK
 snowd     | real             | COOP snowd
 estimated | boolean          | true! :)

Steps:
 1) Compute high+low
 2) Compute precip
 3) Look for snow obs
 4) Initialize entries in the table
 5) Run estimate for Iowa Average Site (IA0000)
"""
import sys
from pyiem import iemre
from pyiem.network import Table as NetworkTable
import datetime
import netCDF4
import numpy as np
from pyiem.datatypes import temperature
import psycopg2.extras
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

state = sys.argv[1]
TABLE = "alldata_%s" % (state, )

HARDCODE = {
    'IA1063': 'BRL',
    'IA1314': 'CID',
    'IA2070': 'DVN',
    'IA2203': 'DSM',
    'IA2367': 'DBQ',
    'IA2723': 'EST',
    'IA4106': 'IOW',
    'IA4587': 'LWD',
    'IA5199': 'MIW',
    'IA5235': 'MCW',
    'IA6389': 'OTM',
    'IA7708': 'SUX',
    'IA7844': 'SPW',
    'IA8706': 'ALO',
    }

# Pre-compute the grid location of each climate site
nt = NetworkTable("%sCLIMATE" % (state.upper(),))
for sid in nt.sts.keys():
    i, j = iemre.find_ij(nt.sts[sid]['lon'], nt.sts[sid]['lat'])
    nt.sts[sid]['gridi'] = i
    nt.sts[sid]['gridj'] = j
    for key in ['high', 'low', 'precip', 'snow', 'snowd']:
        nt.sts[sid][key] = None


def estimate_precip(ts):
    """Estimate precipitation based on IEMRE"""
    idx = iemre.daily_offset(ts)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year, ),
                         'r')
    grid12 = nc.variables['p01d_12z'][idx, :, :] / 25.4
    grid00 = nc.variables['p01d'][idx, :, :] / 25.4
    nc.close()

    for sid in nt.sts.keys():
        if nt.sts[sid]['precip24_hour'] in [0, 22, 23]:
            precip = grid00[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        else:
            precip = grid12[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        # denote trace
        if precip > 0 and precip < 0.01:
            nt.sts[sid]['precip'] = 0.0001
        elif precip < 0:
            nt.sts[sid]['precip'] = 0
        elif np.isnan(precip) or np.ma.is_masked(precip):
            nt.sts[sid]['precip'] = None
        else:
            nt.sts[sid]['precip'] = "%.2f" % (precip,)


def estimate_snow(ts):
    """Estimate the Snow based on COOP reports"""
    idx = iemre.daily_offset(ts)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year, ),
                         'r')
    snowgrid12 = nc.variables['snow_12z'][idx, :, :] / 25.4
    snowdgrid12 = nc.variables['snowd_12z'][idx, :, :] / 25.4
    nc.close()

    for sid in nt.sts.keys():
        val = snowgrid12[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        if val >= 0 and val < 100:
            nt.sts[sid]['snow'] = "%.1f" % (val, )
        val = snowdgrid12[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        if val >= 0 and val < 140:
            nt.sts[sid]['snowd'] = "%.1f" % (val, )


def estimate_hilo(ts):
    """Estimate the High and Low Temperature based on gridded data"""
    idx = iemre.daily_offset(ts)
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year, ),
                         'r')
    highgrid12 = temperature(nc.variables['high_tmpk_12z'][idx, :, :],
                             'K').value('F')
    lowgrid12 = temperature(nc.variables['low_tmpk_12z'][idx, :, :],
                            'K').value('F')
    highgrid00 = temperature(nc.variables['high_tmpk'][idx, :, :],
                             'K').value('F')
    lowgrid00 = temperature(nc.variables['low_tmpk'][idx, :, :],
                            'K').value('F')
    nc.close()

    for sid in nt.sts.keys():
        if nt.sts[sid]['temp24_hour'] in [0, 22, 23]:
            val = highgrid00[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        else:
            val = highgrid12[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        if val > -80 and val < 140:
            nt.sts[sid]['high'] = "%.0f" % (val, )

        if nt.sts[sid]['temp24_hour'] in [0, 22, 23]:
            val = lowgrid00[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        else:
            val = lowgrid12[nt.sts[sid]['gridj'], nt.sts[sid]['gridi']]
        if val > -80 and val < 140:
            nt.sts[sid]['low'] = "%.0f" % (val, )


def commit(ts):
    """
    Inject into the database!
    """
    # Inject!
    for sid in nt.sts.keys():
        if sid[2] == 'C' or sid[2:] == '0000':
            continue
        if nt.sts[sid]['precip'] is None and nt.sts[sid]['high'] is None:
            # print("SID %s skipped due to no data!" % (sid,))
            continue
        # See if we currently have data
        ccursor.execute("""
            SELECT day from """ + TABLE + """
            WHERE station = %s and day = %s
            """, (sid, ts))
        if ccursor.rowcount == 0:
            ccursor.execute("""INSERT INTO """ + TABLE + """
            (station, day, sday, year, month)
            VALUES (%s, %s, %s, %s, %s)
            """, (sid, ts, ts.strftime("%m%d"), ts.year, ts.month))
        sql = """
            UPDATE """ + TABLE + """ SET high = %s, low = %s,
            precip = %s, snow = %s, snowd = %s, estimated = 't'
            WHERE day = %s and station = %s
            """
        args = (nt.sts[sid]['high'], nt.sts[sid]['low'],
                nt.sts[sid]['precip'], nt.sts[sid]['snow'],
                nt.sts[sid]['snowd'], ts, sid)
        ccursor.execute(sql, args)
        if ccursor.rowcount != 1:
            print(("ERROR: %s update of %s %s resulted in %s rows"
                   ) % (TABLE, sid, ts, ccursor.rowcount))


def hardcode(ts):
    """Stations that are hard coded against an ASOS site"""
    for sid in HARDCODE.keys():
        if sid not in nt.sts:
            continue
        icursor.execute("""
        SELECT max_tmpf, min_tmpf, pday from summary s JOIN stations t
        on (t.iemid = s.iemid) WHERE t.id = %s and s.day = %s and
        t.network ~* 'ASOS'
        """, (HARDCODE[sid], ts))
        if icursor.rowcount == 1:
            row = icursor.fetchone()
            if row[0] is not None:
                nt.sts[sid]['high'] = row[0]
            if row[1] is not None:
                nt.sts[sid]['low'] = row[1]
            if row[2] is not None:
                nt.sts[sid]['precip'] = row[2]


def main():
    """main()"""
    dates = []
    today = datetime.date.today()
    if len(sys.argv) == 5:
        dates.append(datetime.date(int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4])))
    else:
        dates.append(today)
        dates.append(datetime.date.today() - datetime.timedelta(days=1))
    for ts in dates:
        estimate_precip(ts)
        estimate_snow(ts)
        estimate_hilo(ts)
        if ts != today:
            hardcode(ts)
        commit(ts)

if __name__ == '__main__':
    ''' See how we are called '''
    main()
    ccursor.close()
    COOP.commit()
    COOP.close()
