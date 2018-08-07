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

HARDCODE = {
    # TODO, the commented out Iowa sites are not long term tracked
    'IA1063': 'BRL',
    # 'IA1314': 'CID',
    # 'IA2070': 'DVN',
    'IA2203': 'DSM',
    # 'IA2367': 'DBQ',
    # 'IA2723': 'EST',
    # 'IA4106': 'IOW',
    # 'IA4587': 'LWD',
    # 'IA5199': 'MIW',
    # 'IA5235': 'MCW',
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

        def do_update():
            """inline."""
            sql = """
                UPDATE """ + table + """ SET high = %s, low = %s,
                precip = %s, snow = %s, snowd = %s, estimated = 't'
                WHERE day = %s and station = %s
                """
            args = (row['high'], row['low'],
                    row['precip'], row['snow'],
                    row['snowd'], ts, sid)
            cursor.execute(sql, args)
        do_update()
        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO """ + table + """
            (station, day, sday, year, month)
            VALUES (%s, %s, %s, %s, %s)
            """, (sid, ts, ts.strftime("%m%d"), ts.year, ts.month))
            do_update()


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
