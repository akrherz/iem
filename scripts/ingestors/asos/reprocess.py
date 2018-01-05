"""
 This script downloads the METAR data provided by wunderground, another script
 than compares it with my current archive and that provided by NSSL to see
 if there are any differences.

Arguments
    python reprocess.py --network=IA_ASOS 1978 1979
    python reprocess.py --station=AMW 1978 1979
    python reprocess.py --monthdate=200003

"""
from __future__ import print_function
import traceback
import datetime
import time
import sys
import os
import re
import subprocess
from optparse import OptionParser

import pytz
import requests
import pandas as pd
from pyiem.datatypes import pressure
from pyiem.util import get_dbconn
from metar.Metar import Metar
from metar.Metar import ParserError as MetarParserError
ASOS = get_dbconn('asos')

SLP = 'Sea Level PressureIn'
ERROR_RE = re.compile("Unparsed groups in body '(?P<msg>.*)' while processing")


class OB(object):
    """hacky representation of the database schema"""
    station = None
    valid = None
    tmpf = None
    dwpf = None
    drct = None
    sknt = None
    alti = None
    gust = None
    vsby = None
    skyc1 = None
    skyc2 = None
    skyc3 = None
    skyc4 = None
    skyl1 = None
    skyl2 = None
    skyl3 = None
    metar = None
    skyl4 = None
    p03i = None
    p06i = None
    p24i = None
    max_tmpf_6hr = None
    min_tmpf_6hr = None
    max_tmpf_24hr = None
    min_tmpf_24hr = None
    mslp = None
    p01i = None
    wxcodes = None


def get_job_list():
    """ Figure out the days and stations we need to get """
    days = []
    stations = []
    tznames = []

    parser = OptionParser()
    parser.add_option("-n", "--network", dest="network",
                      help="IEM network", metavar="NETWORK")
    parser.add_option("-s", "--station", dest="station",
                      help="IEM station", metavar="STATION")
    parser.add_option("-m", "--monthdate", dest="monthdate",
                      help="Month Date", metavar="MONTHDATE")
    (options, args) = parser.parse_args()
    if options.monthdate is not None:
        process_rawtext(options.monthdate)
        return [], []
    now = datetime.date(int(args[0]), 1, 1)
    ets = datetime.date(int(args[1]), 1, 1)
    acursor = ASOS.cursor()
    while now < ets:
        days.append(now)
        now += datetime.timedelta(days=1)
    if options.network is not None:
        sql = """
            SELECT id, archive_begin, tzname from stations
            where network = %s and archive_begin is not null
            ORDER by id ASC
            """
        acursor.execute(sql, (options.network, ))
        floor = days[0] + datetime.timedelta(days=900)
        for row in acursor:
            if row[1].date() > floor:
                print('Skipping station: %4s sts: %s' % (row[0], row[1]))
                continue
            stations.append(row[0])
            tznames.append(row[2])
    else:
        stations.append(options.station)
        sql = """
            SELECT id, archive_begin, tzname from stations
            where id = %s and network ~* 'ASOS'
            """
        acursor.execute(sql, (options.station, ))
        tznames.append(acursor.fetchone()[2])

    print('Processing %s stations for %s days' % (len(stations), len(days)))
    return stations, tznames, days


def workflow():
    """ Do some work """
    stations, tznames, days = get_job_list()

    # Set the show metar option
    jar = requests.cookies.RequestsCookieJar()
    jar.set('Prefs', 'SHOWMETAR:1')

    # Iterate
    removed = 0
    added = 0
    for station, tzname in zip(stations, tznames):
        removed += clear_data(station, tzname, days[0], days[-1])
        added += doit(jar, station, days)
    print(("Total stations: %s removed: %s added: %s"
           ) % (len(stations), removed, added))


def process_rawtext(yyyymm):
    """ Process the raw SAO files the IEM has """
    # skip 0z for now
    sts = datetime.datetime(int(yyyymm[:4]), int(yyyymm[4:]), 1, 1)
    ets = sts + datetime.timedelta(days=32)
    ets = ets.replace(day=1, hour=0)
    interval = datetime.timedelta(hours=1)
    now = sts
    stdata = {}
    while now < ets:
        fn = now.strftime("/mesonet/ARCHIVE/raw/sao/%Y_%m/%y%m%d%H.sao.gz")
        if not os.path.isfile(fn):
            now += interval
            continue
        p = subprocess.Popen(["zcat", fn], stdout=subprocess.PIPE)
        data = p.communicate()[0]
        for product in data.split("\003"):
            tokens = product.split("=")
            for metar in tokens:
                # Dump METARs that have NIL in them
                if metar.find(" NIL") > -1:
                    continue
                elif metar.find("METAR") > -1:
                    metar = metar[metar.find("METAR")+5:]
                elif metar.find("LWIS ") > -1:
                    metar = metar[metar.find("LWIS ")+5:]
                elif metar.find("SPECI") > -1:
                    metar = metar[metar.find("SPECI")+5:]
                metar = " ".join(
                            metar.replace("\r\r\n", " ").strip().split())
                if len(metar.strip()) < 13:
                    continue
                station = metar[:4]
                tm = metar[5:11]
                if metar[11] != 'Z':
                    continue
                if station not in stdata:
                    stdata[station] = {}
                if tm not in stdata[station]:
                    stdata[station][tm] = metar
                else:
                    if len(metar) > len(stdata[station][tm]):
                        stdata[station][tm] = metar
        now += interval

    for station in stdata.keys():
        if len(station) == 0:
            continue
        times = stdata[station].keys()
        times.sort()
        day = "00"
        out = None
        for tm in times:
            if tm[:2] != day:
                if out is not None:
                    out.close()
                day = tm[:2]
                dirname = "/mesonet/ARCHIVE/wunder/cache/%s/%s/" % (
                                            stup(station), yyyymm[:4])
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                fn = "%s/%s%s.txt" % (dirname, yyyymm, day)
                if os.path.isfile(fn) and len(open(fn).read()) > 500:
                    out = open('/dev/null', 'a')
                else:
                    try:
                        out = open(fn, 'w')
                    except Exception as exp:
                        continue
                    out.write("FullMetar,\n")
            if out is not None and not out.closed:
                out.write("%s,\n" % (stdata[station][tm],))


def stup(station):
    if station[0] == 'K':
        return station[1:]
    return station


def clear_data(station, tzname, sts, ets):
    if tzname is None:
        tzname = 'UTC'
    acursor = ASOS.cursor()
    ets = ets + datetime.timedelta(days=1)
    acursor.execute("""
        DELETE from alldata WHERE station = %s and
        valid at time zone %s >= %s and (valid at time zone %s) < %s
        and report_type = 2
    """, (station, tzname, sts, tzname, ets))
    cnt = acursor.rowcount
    print(('Removed %s rows for station %s %s->%s(%s)'
           ) % (cnt, station, sts, ets, tzname))
    ASOS.commit()
    return cnt


def to_df(html):
    """Make a dataframe from this html"""
    if html.find('obsTable') == -1:
        return None
    df = pd.read_html(html, attrs=dict(id='obsTable'))[0]
    # OK, we should have a round number of rows with the METAR coming below
    # the observation line
    if len(df.index) % 2 != 0:
        raise Exception(("ERROR: dataframe has %s (odd) number of rows"
                         ) % (len(df.index),))
    resdf = pd.DataFrame({
        'FullMetar': df.iloc[1::2, :]['Temp.'].values,
        'Sea Level PressureIn': df.iloc[::2, :]['Pressure'].values})
    resdf['Sea Level PressureIn'] = resdf['Sea Level PressureIn'].str.replace(
                                        '\xa0in', '')
    return resdf


def read_legacy(fn):
    data = open(fn).read()
    lines = data.split("\n")
    headers = None
    rows = []
    for line in lines:
        line = line.replace("<br />", "").replace("\xff", "")
        if line.strip() == "":
            continue
        tokens = line.split(",")
        if headers is None:
            headers = {}
            for i in range(len(tokens)):
                headers[tokens[i]] = i
            continue
        if "FullMetar" in headers and len(tokens) >= headers["FullMetar"]:
            mstr = (tokens[headers["FullMetar"]]
                    ).strip().replace("'",
                                      "").replace("SPECI ",
                                                  "").replace("METAR ", "")
            pres = None
            if SLP in headers:
                value = tokens[headers[SLP]].strip()
                if value not in ['-', '']:
                    try:
                        pres = float(value)
                    except Exception as exp:
                        print(("Failed to parse SLP: %s %s"
                               ) % (repr(headers[SLP]), fn))
            rows.append({'FullMetar': mstr,
                         'Sea Level PressureIn': pres})
    return pd.DataFrame(rows)


def get_df(station, now, jar):
    """Return the dataframe for this station and date"""
    mydir = "/mesonet/ARCHIVE/wunder/cache/%s/%s/" % (station, now.year)
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    fn = "%s%s.txt" % (mydir, now.strftime("%Y%m%d"))
    if os.path.isfile(fn) and len(open(fn).read()) > 140:
        return read_legacy(fn)

    faa = "K%s" % (station,) if len(station) == 3 else station
    # Fetch it
    url = ("https://www.wunderground.com/history/airport/%s/%s/%-i/%-i/"
           "DailyHistory.html") % (faa, now.year, now.month,
                                   now.day)
    try:
        res = requests.get(url, timeout=30, cookies=jar)
        time.sleep(1)  # throttle
        if res.status_code != 200:
            time.sleep(5)  # allow for transient server errors to subside?
            raise Exception("%s -> %s" % (url, res.status_code))
        df = to_df(res.content)
        if df is None:
            return None
        df.to_csv(fn, index=False, encoding='utf-8')
    except KeyboardInterrupt:
        sys.exit()
    except ValueError:
        print("ValueError %s %s" % (station, now))
        return None
    except Exception as exp:
        print("Failure %s %s" % (station, now))
        traceback.print_exc()
        return None
    return df


def doit(jar, station, days):
    """ Fetch! """
    valids = []
    inserts = 0
    baddays = 0
    acursor = ASOS.cursor()
    for now in days:
        if now.month == 1 and now.day == 1:
            valids = []
        df = get_df(station, now, jar)
        if df is None:
            baddays += 1
            continue
        for _, row in df.iterrows():
            ob = process_metar(row['FullMetar'], now)
            if ob is None or ob.valid in valids:
                continue
            valids.append(ob.valid)

            # Account for SLP505 actually being 1050.5 and not 950.5 :(
            if SLP in row:
                try:
                    pres = pressure(row['Sea Level PressureIn'].value, "IN")
                    diff = pres.value("MB") - ob.mslp
                    if abs(diff) > 25:
                        oldval = ob.mslp
                        ob.mslp = "%.1f" % (pres.value("MB"),)
                        ob.alti = row['Sea Level PressureIn'].value
                        print(('SETTING PRESSURE %s old: %s new: %s'
                               ) % (ob.valid.strftime("%Y/%m/%d %H%M"),
                                    oldval, ob.mslp))
                except Exception as _exp:
                    pass

            sql = """
                INSERT into t""" + str(ob.valid.year) + """ (station, valid,
                tmpf, dwpf, vsby, drct, sknt, gust, p01i, alti, skyc1, skyc2,
                skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar, mslp,
                wxcodes, p03i, p06i, p24i, max_tmpf_6hr, max_tmpf_24hr,
                min_tmpf_6hr, min_tmpf_24hr, report_type)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, 2)
            """
            try:
                cmtr = ob.metar.decode('utf-8', 'replace').encode('ascii',
                                                                  'replace')
            except Exception as exp:
                print(exp)
                print("Non-ASCII METAR? %s" % (repr(ob.metar),))
                continue
            args = (station, ob.valid, ob.tmpf, ob.dwpf, ob.vsby, ob.drct,
                    ob.sknt, ob.gust, ob.p01i, ob.alti, ob.skyc1, ob.skyc2,
                    ob.skyc3, ob.skyc4, ob.skyl1, ob.skyl2, ob.skyl3,
                    ob.skyl4, cmtr,
                    ob.mslp, ob.wxcodes, ob.p03i,
                    ob.p06i, ob.p24i, ob.max_tmpf_6hr, ob.max_tmpf_24hr,
                    ob.min_tmpf_6hr, ob.min_tmpf_24hr)

            acursor.execute(sql, args)
            inserts += 1
            if inserts % 1000 == 0:
                acursor.close()
                ASOS.commit()
                acursor = ASOS.cursor()
    acursor.close()
    ASOS.commit()
    acursor = ASOS.cursor()
    print("%s Days:%s/%s Inserts: %s" % (station, len(days) - baddays,
                                         len(days), inserts))
    return inserts


def process_metar(mstr, now):
    """ Do the METAR Processing """
    mtr = None
    while mtr is None:
        try:
            mtr = Metar(mstr, now.month, now.year)
        except MetarParserError as exp:
            try:
                msg = str(exp)
            except Exception as exp:
                return None
            if msg.find("day is out of range for month") > 0 and now.day == 1:
                now -= datetime.timedelta(days=1)
                continue
            tokens = ERROR_RE.findall(str(exp))
            orig_mstr = mstr
            if tokens:
                for token in tokens[0].split():
                    mstr = mstr.replace(" %s" % (token, ), "")
                if orig_mstr == mstr:
                    print("Can't fix badly formatted metar: " + mstr)
                    return None
            else:
                print("MetarParserError: "+msg)
                print("    --> now: %s month: %s, year: %s" % (now, now.month,
                                                               now.year))
                sys.exit()
                return None
        except Exception, exp:
            print("Double Fail: %s %s" % (mstr, exp))
            return None
    if mtr is None or mtr.time is None:
        return None

    ob = OB()
    ob.metar = mstr[:254]

    gts = datetime.datetime(mtr.time.year, mtr.time.month,
                            mtr.time.day, mtr.time.hour, mtr.time.minute)
    gts = gts.replace(tzinfo=pytz.timezone("UTC"))
    # When processing data on the last day of the month, we get GMT times
    # for the first of this month
    if gts.day == 1 and now.day > 10:
        tm = now + datetime.timedelta(days=1)
        gts = gts.replace(year=tm.year, month=tm.month, day=tm.day)

    ob.valid = gts

    if mtr.temp:
        ob.tmpf = mtr.temp.value("F")
    if mtr.dewpt:
        ob.dwpf = mtr.dewpt.value("F")

    if mtr.wind_speed:
        ob.sknt = mtr.wind_speed.value("KT")
    if mtr.wind_gust:
        ob.gust = mtr.wind_gust.value("KT")

    if mtr.wind_dir and mtr.wind_dir.value() != "VRB":
        ob.drct = mtr.wind_dir.value()

    if mtr.vis:
        ob.vsby = mtr.vis.value("SM")

    if mtr.press:
        ob.alti = mtr.press.value("IN")

    if mtr.press_sea_level:
        ob.mslp = mtr.press_sea_level.value("MB")

    if mtr.precip_1hr:
        ob.p01i = mtr.precip_1hr.value("IN")

    # Do something with sky coverage
    for i in range(len(mtr.sky)):
        (c, h, _) = mtr.sky[i]
        setattr(ob, 'skyc%s' % (i+1), c)
        if h is not None:
            setattr(ob, 'skyl%s' % (i+1), h.value("FT"))

    if mtr.max_temp_6hr:
        ob.max_tmpf_6hr = mtr.max_temp_6hr.value("F")
    if mtr.min_temp_6hr:
        ob.min_tmpf_6hr = mtr.min_temp_6hr.value("F")
    if mtr.max_temp_24hr:
        ob.max_tmpf_24hr = mtr.max_temp_24hr.value("F")
    if mtr.min_temp_24hr:
        ob.min_tmpf_6hr = mtr.min_temp_24hr.value("F")
    if mtr.precip_3hr:
        ob.p03i = mtr.precip_3hr.value("IN")
    if mtr.precip_6hr:
        ob.p06i = mtr.precip_6hr.value("IN")
    if mtr.precip_24hr:
        ob.p24i = mtr.precip_24hr.value("IN")

    # Presentwx
    if mtr.weather:
        pwx = []
        for x in mtr.weather:
            pwx.append(("").join([a for a in x if a is not None]))
        ob.wxcodes = pwx

    return ob


def main():
    """Go Main Go"""
    print('Starting up...')
    workflow()
    ASOS.commit()
    ASOS.close()
    print('Done!')


if __name__ == "__main__":
    main()
