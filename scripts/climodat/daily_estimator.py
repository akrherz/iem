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
from __future__ import print_function
import sys
import datetime

from pyiem import iemre
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pyiem.datatypes import temperature
import netCDF4
import numpy as np
import psycopg2.extras

COOP = get_dbconn('coop')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
IEM = get_dbconn('iem')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

state = sys.argv[1]
TABLE = "alldata_%s" % (state, )

"""
with inn as (
 select climate_site, id, name from stations where network = 'NWSCLI'
 and state = 'OH' ORDER by id)

 SELECT i.climate_site, i.id, s.name, i.name from
 inn i JOIN stations s on (i.climate_site = s.id);
"""

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

    # Illinois
    'IL0338': 'ARR',
    'IL8740': 'CMI',
    'IL2193': 'DEC',
    'IL5079': 'ILX',
    'IL1577': 'MDW',
    'IL5751': 'MLI',
    'IL5430': 'MTO',
    'IL1549': 'ORD',
    'IL6711': 'PIA',
    'IL7382': 'RFD',
    'IL8179': 'SPI',
    'IL7072': 'UIN',
    # KDPA | IL2736       | CHICAGO/DUPAGE
    # KLOT | IL4530       | ROMEOVILLE/CHI
    # KLWV | IL6558       | LAWRENCEVILLE
    # KUGN | IL1549       | WAUKEGAN

    # Indiana
    'IN0784': 'BMG',
    'IN2738': 'EVV',
    'IN3037': 'FWA',
    'IN7999': 'GEZ',
    # IN0877       | KHUF | BOWLING GREEN 1 W           | TERRE HAUTE
    'IN4259': 'IND',
    # IN9430       | KLAF | WEST LAFAYETTE 6 NW         | LAFAYETTE
    'IN6023': 'MIE',
    'IN8187': 'SBN',
    # IN4837       | KVPZ | LAPORTE                     | VALPARAISO

    # Kansas
    'KS8830': 'ICT',
    'KS2164': 'DDC',
    'KS3153': 'GLD',
    'KS4559': 'LWC',
    'KS4972': 'MHK',
    'KS7160': 'SLN',
    'KS8167': 'TOP',
    'KS1767': 'CNK',
    # KCNU | KS3984       | CHANUTE
    # KEMP | KS4937       | EMPORIA
    # KGCK | KS2980       | GARDEN_CITY
    # KHLC | KS8498       | HILL_CITY
    # KOJC | KS7809       | OLATHE (OJC)
    # KP28 | KS6549       | MEDICINE_LODGE

    # Kentucky
    'KY0909': 'BWG',
    'KY1855': 'CVG',
    # KY4746       | KFFT | LEXINGTON BLUEGRASS AP     | CAPITAL CITY AIRPORT/F
    'KY6110': 'JKL',
    'KY4746': 'LEX',
    # KY4954       | KLOU | LOUISVILLE INTL AP         | LOUISVILLE/BOWMAN
    # KY0381       | KLOZ | BARBOURVILLE               | LONDON-CORBIN ARPT
    'KY4202': 'PAH',
    'KY4954': 'SDF',

    # Michigan
    'MI7366': 'ANJ',
    'MI0164': 'APN',
    # MI3504       | KAZO | GULL LK BIOLOGICAL STN        | KALAMAZOO
    'MI3858': 'BIV',
    'MI0552': 'BTL',
    'MI2103': 'DTW',
    'MI2846': 'FNT',
    'MI3333': 'GRR',
    'MI3932': 'HTL',
    'MI4150': 'JXN',
    'MI4641': 'LAN',
    'MI7227': 'MBS',
    'MI5712': 'MKG',
    'MI5178': 'MQT',
    # MI5097       | KTVC | MAPLE CITY 1E                 | TRAVERSE CIT

    # Minnesota
    'MN2248': 'DLH',
    'MN4026': 'INL',
    # MN4176       | KMPX | JORDAN 1SSW            | Minneapolis NWS
    'MN5435': 'MSP',
    'MN7004': 'RST',
    'MN7294': 'STC',

    # Missouri
    # MO4226       | KCGI | JACKSON                  | CAPE GIRARDEAU
    'MO1791': 'COU',
    'MO7632': 'DMO',
    'MO4544': 'IRK',
    # MO8664       | KJLN | WACO 4N                  | Joplin
    'MO4359': 'MCI',
    'MO7976': 'SGF',
    # MO6357       | KSTJ | OREGON                   | ST. JOSEPH
    'MO7455': 'STL',
    'MO8880': 'UNO',
    # MO7263       | KVIH | ROLLA UNI OF MISSOURI    | VICHY/ROLLA

    # Nebraska
    'NE0130': 'AIA',
    'NE1200': 'BBW',
    'NE7665': 'BFF',
    'NE1575': 'CDR',
    'NE4335': 'EAR',
    'NE3395': 'GRI',
    'NE3660': 'HSI',
    'NE4110': 'IML',
    'NE6065': 'LBF',
    # NE5105       | KLNK | MALCOLM                | LINCOLN
    'NE5310': 'MCK',
    # NE3050       | KOAX | FREMONT                | Omaha - Valley
    # NE2770       | KODX | ERICSON 8 WNW          | ORD/SHARP FIELD
    'NE5995': 'OFK',
    'NE6255': 'OMA',
    'NE7830': 'SNY',
    'NE8760': 'VTN',

    # North Dakota
    'ND0819': 'BIS',
    # ND2183       | KDIK | THEODORE ROOSEVELT AP     | DICKINSON
    'ND2859': 'FAR',
    # ND3621       | KFGF | GRAND FORKS UNIV NWS      | Grand Forks NWS
    'ND3616': 'GFK',
    # ND7450       | KHEI | REEDER                    | HETTINGER
    'ND9425': 'ISN',
    'ND4413': 'JMS',
    'ND5988': 'MOT',
    'ND3376': 'N60',

    # Ohio
    'OH0058': 'CAK',
    'OH1657': 'CLE',
    'OH1786': 'CMH',
    'OH2075': 'DAY',
    'OH4865': 'MFD',
    # OH1905       | KPHD | COSHOCTON AG RSCH STN         | NEW PHILADELPHIA
    'OH8357': 'TOL',
    'OH9406': 'YNG',
    'OH9417': 'ZZV',

    # South Dakota
    # SD5048       | K2WX | LUDLOW 3 SSE         | BUFFALO
    'SD7742': '8D3',
    'SD0020': 'ABR',
    'SD8932': 'ATY',
    'SD2087': 'CUT',
    'SD2852': 'D07',
    'SD7667': 'FSD',
    'SD4127': 'HON',
    'SD9367': 'ICR',
    # SD6212       | KIEN | OELRICHS             | PINE RIDGE
    'SD5691': 'MBG',
    'SD6936': 'MHE',
    # SD1972       | KPHP | COTTONWOOD 2 E       | PHILIP
    'SD6597': 'PIR',
    'SD6947': 'RAP',
    # SD6947       | KUNR | RAPID CITY 4NW       | Rapid City

    # Wisconsin
    'WI5479': 'MKE',
    'WI3269': 'GRB',
    'WI7113': 'RHI',
    'WI2428': 'EAU',
    'WI4961': 'MSN',
    'WI4370': 'LSE',
    'WI8968': 'AUW',
    }

# Pre-compute the grid location of each climate site
nt = NetworkTable("%sCLIMATE" % (state.upper(),))


def load_table():
    """Update the station table"""
    for sid in nt.sts:
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

    for sid in nt.sts:
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

    for sid in nt.sts:
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
    for sid in HARDCODE:
        if sid not in nt.sts:
            if sid[:2] == state:
                print(("daily_estimator has sid %s configured, but no table?"
                       ) % (sid, ))
            continue
        icursor.execute("""
        SELECT max_tmpf, min_tmpf, pday, snow from summary s JOIN stations t
        on (t.iemid = s.iemid) WHERE t.id = %s and s.day = %s and
        t.network = %s
        """, (HARDCODE[sid], ts, state + "_ASOS"))
        if icursor.rowcount == 1:
            row = icursor.fetchone()
            if row[0] is not None:
                nt.sts[sid]['high'] = row[0]
            if row[1] is not None:
                nt.sts[sid]['low'] = row[1]
            if row[2] is not None:
                nt.sts[sid]['precip'] = row[2]
            if row[3] is not None:
                nt.sts[sid]['snow'] = row[3]


def main():
    """main()"""
    load_table()
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
    # See how we are called
    main()
    ccursor.close()
    COOP.commit()
    COOP.close()
