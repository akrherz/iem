"""The Daily Processor of Wx Data for Yield Forecast Project

 - Read the baseline from the database
 - Add columns GDD(F) ST4(C) ST12 ST24 ST50 SM12[frac] SM24 SM50
 - For each year, replace the Jan 1 to yesterday data with actual data
 - Replace today to day + 3 with forecast data
 - For this year, replace day + 4 to Dec 31 with CFS :)
 - Upload the resulting file <site>_YYYYmmdd.met
"""
import dropbox
import sys
import datetime
import numpy as np
import pandas as pd
import tempfile
from pandas.io.sql import read_sql
from pyiem.datatypes import temperature, distance
from pyiem.meteorology import gdd
import psycopg2
import os
import subprocess
from pyiem.util import get_properties

XREF = {'ames': {'isusm': 'BOOI4', 'climodat': 'IA0200'},
        'cobs': {'isusm': 'BOOI4', 'climodat': 'IA0200'},
        'crawfordsville': {'isusm': 'CRFI4', 'climodat': 'IA8688'},
        'lewis': {'isusm': 'OKLI4', 'climodat': 'IA0364'},
        'nashua': {'isusm': 'NASI4', 'climodat': 'IA1402'},
        'sutherland': {'isusm': 'CAMI4', 'climodat': 'IA1442'}}


def p(val, prec):
    if val is None or np.isnan(val):
        return '?'
    _fmt = "%%.%sf" % (prec,)
    return _fmt % (val,)


def write_and_upload(df, location):
    """ We are done, whew!"""
    props = get_properties()
    dbx = dropbox.Dropbox(props.get('dropbox.token'))
    (tmpfd, tmpfn) = tempfile.mkstemp()
    for line in open("baseline/%s.txt" % (location, )):
        if line.startswith("year"):
            break
        os.write(tmpfd, line.strip()+"\r\n")
    os.write(tmpfd, ('! auto-generated at %sZ by daryl akrherz@iastate.edu\r\n'
                     ) % (datetime.datetime.utcnow().isoformat(),))
    fmt = ("%-10s%-10s%-10s%-10s%-10s%-10s"
           "%-10s%-10s%-10s%-10s%-10s%-10s%-10s%-10s\r\n")
    os.write(tmpfd, fmt % ('year', 'day', 'radn', 'maxt', 'mint', 'rain',
                           'gdd', 'st4', 'st12', 'st24', 'st50',
                           'sm12', 'sm24', 'sm50'))
    os.write(tmpfd, fmt % ('()', '()', '(MJ/m^2)', '(oC)', '(oC)', '(mm)',
                           '(oF)', '(oC)', '(oC)', '(oC)', '(oC)',
                           '(mm/mm)', '(mm/mm)', '(mm/mm)'))
    fmt = (" %-9i%-10i%-10s%-10s%-10s%-10s%-10s"
           "%-10s%-10s%-10s%-10s%-10s%-10s%-10s\r\n")
    for valid, row in df.iterrows():
        os.write(tmpfd, fmt % (valid.year,
                               int(valid.strftime("%j")),
                               p(row['radn'], 3),
                               p(row['maxt'], 1), p(row['mint'], 1),
                               p(row['rain'], 2),
                               p(row['gdd'], 1), p(row['st4'], 2),
                               p(row['st12'], 2),
                               p(row['st24'], 2), p(row['st50'], 2),
                               p(row['sm12'], 2),
                               p(row['sm24'], 2), p(row['sm50'], 2)))
    os.close(tmpfd)

    today = datetime.date.today()
    remotefn = "%s_%s.met" % (location, today.strftime("%Y%m%d"))
    dbx.files_upload(open(tmpfn).read(),
                     "/YieldForecast/Daryl/%s" % (remotefn, ),
                     mode=dropbox.files.WriteMode.overwrite)
    # Save file for usage by web plotting...
    os.chmod(tmpfn, 0644)
    # os.rename fails here due to cross device link bug
    subprocess.call(("mv %s /mesonet/share/pickup/yieldfx/%s.txt"
                     ) % (tmpfn, location), shell=True)


def qc(df):
    """Run some QC against the dataframe"""
    # Make sure our frame is sorted
    df.sort_index(inplace=True)


def load_baseline(location):
    """return a dataframe of this location's data"""
    pgconn = psycopg2.connect(database='coop', host='iemdb')
    df = read_sql("""
        SELECT *, extract(doy from valid) as doy,
        extract(year from valid) as year
        from yieldfx_baseline where station = %s ORDER by valid
        """, pgconn, params=(location,), index_col='valid')
    # we want data from 1980 to this year
    today = datetime.date.today()
    dec31 = today.replace(month=12, day=31)
    df = df.reindex(index=pd.date_range(datetime.date(1980, 1, 1), dec31).date)
    return df


def replace_forecast(df, location):
    """Replace dataframe data with forecast for this location"""
    pgconn = psycopg2.connect(database='coop', host='iemdb')
    cursor = pgconn.cursor()
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    coop = XREF[location]['climodat']
    years = [int(y) for y in np.arange(df.index.values.min().year,
                                       df.index.values.max().year + 1)]
    if jan1.year in years:
        years.remove(jan1.year)
    cursor.execute("""
        SELECT day, high, low, precip from alldata_forecast WHERE
        modelid = (SELECT id from forecast_inventory WHERE model = 'NDFD'
        ORDER by modelts DESC LIMIT 1) and station = %s and day >= %s
    """, (coop, today))
    rcols = ['maxt', 'mint', 'rain']
    for row in cursor:
        valid = row[0]
        maxc = temperature(row[1], 'F').value('C')
        minc = temperature(row[2], 'F').value('C')
        rain = distance(row[3], 'IN').value('MM')
        for year in years:
            df.loc[valid.replace(year=year), rcols] = (maxc, minc, rain)


def replace_cfs(df, location):
    """Replace the CFS data for this year!"""
    pgconn = psycopg2.connect(database='coop', host='iemdb')
    cursor = pgconn.cursor()
    coop = XREF[location]['climodat']
    today = datetime.date.today() + datetime.timedelta(days=3)
    dec31 = today.replace(day=31, month=12)
    cursor.execute("""
        SELECT day, high, low, precip, srad from alldata_forecast WHERE
        modelid = (SELECT id from forecast_inventory WHERE model = 'CFS'
        ORDER by modelts DESC LIMIT 1) and station = %s and day >= %s
        and day <= %s
    """, (coop, today, dec31))
    rcols = ['maxt', 'mint', 'rain', 'radn']
    for row in cursor:
        maxt = temperature(row[1], 'F').value('C')
        mint = temperature(row[2], 'F').value('C')
        rain = distance(row[3], 'IN').value('MM')
        radn = row[4]
        df.loc[row[0], rcols] = [maxt, mint, rain, radn]


def replace_obs(df, location):
    """Replace dataframe data with obs for this location

    Tricky part, if the baseline already provides data for this year, we should
    use it!
    """
    pgconn = psycopg2.connect(database='isuag', host='iemdb')
    cursor = pgconn.cursor()
    isusm = XREF[location]['isusm']
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    years = [int(y) for y in np.arange(df.index.values.min().year,
                                       df.index.values.max().year + 1)]
    # TODO: support the ugliness of Leap day
    cursor.execute("""
        select valid, tair_c_max, tair_c_min, slrmj_tot, vwc_12_avg,
        vwc_24_avg, vwc_50_avg, tsoil_c_avg, t12_c_avg, t24_c_avg, t50_c_avg
        from sm_daily WHERE station = %s and valid >= %s and
        to_char(valid, 'mmdd') != '0229'
        """, (isusm, jan1))
    rcols = ['maxt', 'mint', 'radn', 'gdd', 'sm12', 'sm24', 'sm50',
             'st4', 'st12', 'st24', 'st50', ]
    for row in cursor:
        valid = row[0]
        _gdd = gdd(temperature(row[1], 'C'), temperature(row[2], 'C'))
        for year in years:
            if (year == jan1.year and
                    not np.isnan(df.at[valid.replace(year=jan1.year),
                                       'maxt'])):
                df.loc[valid.replace(year=year),
                       rcols[3:]] = (_gdd, row[4], row[5],
                                     row[6], row[7], row[8],
                                     row[9], row[10])
                continue
            df.loc[valid.replace(year=year), rcols] = (row[1], row[2], row[3],
                                                       _gdd, row[4], row[5],
                                                       row[6], row[7], row[8],
                                                       row[9], row[10])
    # Go get precip from Climodat
    coop = XREF[location]['climodat']
    pgconn = psycopg2.connect(database='coop', host='iemdb')
    cursor = pgconn.cursor()
    cursor.execute("""
        SELECT day, precip from alldata_ia where year = %s and station = %s
        and day < %s and sday != '0229'
        """, (jan1.year, coop, today))
    for row in cursor:
        valid = row[0]
        pcpn = distance(row[1], 'IN').value('MM')
        for year in years:
            df.at[valid.replace(year=year), 'rain'] = pcpn


def compute_gdd(df):
    """Compute GDDs Please"""
    df['gdd'] = gdd(temperature(df['maxt'], 'C'), temperature(df['mint'], 'C'))


def do(location):
    """Workflow for a particular location"""
    # 1. Read baseline
    df = load_baseline(location)
    # 2. Add columns and observed data
    for colname in ['gdd', 'st4', 'st12', 'st24', 'st50', 'sm12', 'sm24',
                    'sm50']:
        df[colname] = None
    # 3. Do data replacement
    # TODO: what to do with RAIN!
    replace_obs(df, location)
    # 4. Add forecast data
    replace_forecast(df, location)
    # 5. Add CFS for this year
    replace_cfs(df, location)
    # 6. Compute GDD
    compute_gdd(df)
    # 7. QC
    qc(df)
    # 8. Write and upload the file
    write_and_upload(df, location)


def main(argv):
    """Do Something"""
    for location in XREF:
        do(location)

if __name__ == '__main__':
    main(sys.argv)
