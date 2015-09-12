"""
Collect up schoolnet data into files we have for outgoing...
"""
import sys
import os
import datetime
from pyiem.network import Table as NetworkTable
import pyiem.meteorology as meteorology
from pyiem.datatypes import temperature, speed
import pyiem.util as util
import psycopg2.extras
import subprocess
import tempfile
import calendar
import pytz

utc = datetime.datetime.utcnow()
utc = utc.replace(tzinfo=pytz.timezone("UTC"))
tstr = utc.strftime("%Y%m%d%H%M")

now = utc.astimezone(pytz.timezone("America/Chicago"))

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

st = NetworkTable(['KCCI', 'KELO', 'KIMT'])

st.sts["SMAI4"]["plot_name"] = "M-town"
st.sts["SBZI4"]["plot_name"] = "Zoo"
st.sts["SMSI4"]["plot_name"] = "Barnum"
st.sts["STQI4"]["plot_name"] = "Tama"
st.sts["SBOI4"]["plot_name"] = "Boone"


def altiTxt(d):
    if d == "":
        return "S"
    if d < 0:
        return "F"
    if d > 0:
        return "R"
    return "S"


def computeOthers(d):
    r = {}
    # Need something to compute other values needed for output
    for sid in d.keys():
        ob = d[sid]
        ob["ticks"] = calendar.timegm(ob['utc_valid'].timetuple())
        if ob['sknt'] is not None:
            ob["sped"] = ob["sknt"] * 1.17
        if ob.get('tmpf') is not None and ob.get('dwpf') is not None:
            tmpf = temperature(ob['tmpf'], 'F')
            dwpf = temperature(ob['dwpf'], 'F')
            ob["relh"] = meteorology.relh(tmpf, dwpf).value('%')
        else:
            ob['relh'] = None
        if ob['relh'] == 'M':
            ob['relh'] = None

        if (ob.get('tmpf') is not None and ob.get('dwpf') is not None and
                ob.get('sped') is not None):
            tmpf = temperature(ob['tmpf'], 'F')
            dwpf = temperature(ob['dwpf'], 'F')
            sknt = speed(ob['sped'], 'MPH')
            ob["feel"] = meteorology.feelslike(tmpf, dwpf, sknt).value("F")
        else:
            ob['feel'] = None
        if ob['feel'] == 'M':
            ob['feel'] = None

        ob["altiTend"] = 'S'
        ob["drctTxt"] = util.drct2text(ob["drct"])
        if ob["max_drct"] is None:
            ob["max_drct"] = 0
        ob["max_drctTxt"] = util.drct2text(ob["max_drct"])
        ob["20gu"] = 0
        if ob['gust'] is not None:
            ob["gmph"] = ob["gust"] * 1.17
        if ob['max_gust'] is not None:
            ob["max_sped"] = ob["max_gust"] * 1.17
        else:
            ob['max_sped'] = 0
        ob['pday'] = 0 if ob['pday'] is None else ob['pday']
        ob['pmonth'] = 0 if ob['pmonth'] is None else ob['pmonth']
        ob["gtim"] = "0000"
        ob["gtim2"] = "12:00 AM"
        if ob["max_gust_ts"] is not None and ob["max_gust_ts"] != "null":
            ob["gtim"] = ob["max_gust_ts"].strftime("%H%M")
            ob["gtim2"] = ob["max_gust_ts"].strftime("%-I:%M %p")
        r[sid] = ob
    return r


def get_precip_totals(obs, network):
    now = datetime.datetime.now()
    for dy in [2, 3, 7, 14]:
        sql = """SELECT id, sum(pday) as rain from summary s JOIN stations t
            ON (t.iemid = s.iemid) WHERE
            network = '%s' and day > '%s' and pday >= 0 GROUP by id
            """ % (network,
                   (now - datetime.timedelta(days=dy)).strftime("%Y-%m-%d"))
        icursor.execute(sql)
        for row in icursor:
            obs[row["id"]]["p%sday" % (dy,)] = (row["rain"]
                                                if row['rain'] is not None
                                                else 0)


def formatter(val, precision, mval='M'):
    if val is None or isinstance(val, str):
        return mval
    fmt = '%%.%sf' % (precision,)
    return fmt % val


def get_network(network):
    obs = {}
    icursor.execute("""
    SELECT c.*, s.*, t.id, t.name as sname,
    c.valid at time zone 'UTC' as utc_valid
    from current c, summary s, stations t WHERE
    t.iemid = s.iemid and s.iemid = c.iemid and t.network = '%s' and
    s.day = 'TODAY' ORDER by random()
    """ % (network, ))
    for row in icursor:
        obs[row['id']] = row.copy()
    return obs


def main():
    kcci = get_network("KCCI")
    kelo = get_network("KELO")
    kimt = get_network("KIMT")

    get_precip_totals(kcci, 'KCCI')
    get_precip_totals(kelo, 'KELO')
    get_precip_totals(kimt, 'KIMT')
    computeOthers(kcci)
    computeOthers(kelo)
    computeOthers(kimt)

    tmpfp = tempfile.mktemp()
    of = open(tmpfp, 'w')
    of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,")
    of.write("drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,")
    of.write("drct_max,max_sped,max_drctTxt,max_srad\n")
    for sid in kcci.keys():
        v = kcci[sid]
        try:
            s = ("%s,%s,%s,%s,%s,"
                 "") % (v.get('id'),
                        v.get('ticks'), formatter(v.get('tmpf'), 0, -99),
                        formatter(v.get('dwpf'), 0, -99),
                        formatter(v.get('relh'), 0, -99))
            s += "%s,%s,%s,%s," % (formatter(v.get('feel'), 0, -99),
                                   formatter(v.get('pres'), 2, -99),
                                   v.get('altiTend'), v.get('drctTxt'))
            s += "%s,%s,%s,%s," % (formatter(v.get('sped'), 0, -99),
                                   formatter(v.get('sknt'), 0, -99),
                                   formatter(v.get('drct'), 0, -99),
                                   formatter(v.get('20gu'), 0, -99))
            s += "%s,%s,%s,%s," % (formatter(v.get('gmph'), 0, -99),
                                   v.get('gtim'),
                                   formatter(v.get('pday'), 2, -99),
                                   formatter(v.get('pmonth'), 2, -99))
            s += "%s,%s,%s," % (formatter(v.get('sknt'), 0, -99),
                                formatter(v.get('drct'), 0, -99),
                                formatter(v.get('20gu'), 0, -99))
            s += "%s,%s,%s,%s\n" % (formatter(v.get('max_drct'), 0, -99),
                                    formatter(v.get('max_sped'), 0, -99),
                                    v.get('max_drctTxt'),
                                    formatter(v.get('max_srad'), 0, -99))
            of.write(s.replace("'", ""))
        except:
            print kcci[sid]
            print sys.excepthook(sys.exc_info()[0],
                                 sys.exc_info()[1], sys.exc_info()[2])
            sys.exc_traceback = None

    of.close()
    subprocess.call(("/home/ldm/bin/pqinsert -p 'data c %s csv/kcci.dat "
                     "bogus dat' %s") % (tstr, tmpfp), shell=True)
    os.remove(tmpfp)

    of = open(tmpfp, 'w')

    of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,")
    of.write("drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,")
    of.write("drct_max,max_sped,max_drctTxt,srad,max_srad,online\n")
    for sid in kcci.keys():
        v = kcci[sid]
        v['online'] = 1
        if (now - v['valid']).seconds > 3600:
            v['online'] = 0
        try:
            s = "%s,%s,%s,%s,%s," % (v.get('id'),
                                     v.get('ticks'),
                                     formatter(v.get('tmpf'), 0),
                                     formatter(v.get('dwpf'), 0),
                                     formatter(v.get('relh'), 0))
            s += "%s,%s,%s,%s," % (formatter(v.get('feel'), 0),
                                   formatter(v.get('pres'), 2),
                                   v.get('altiTend'), v.get('drctTxt'))
            s += "%s,%s,%s,%s," % (formatter(v.get('sped'), 0),
                                   formatter(v.get('sknt'), 0),
                                   formatter(v.get('drct'), 0),
                                   formatter(v.get('20gu'), 0))
            s += "%s,%s,%s,%s," % (formatter(v.get('gmph'), 0),
                                   v.get('gtim'),
                                   formatter(v.get('pday'), 2),
                                   formatter(v.get('pmonth'), 2))
            s += "%s,%s,%s," % (formatter(v.get('sknt'), 0),
                                formatter(v.get('drct'), 0),
                                formatter(v.get('20gu'), 0))
            s += "%s,%s,%s,%s,%s,%s\n" % (formatter(v.get('max_drct'), 0),
                                          formatter(v.get('max_sped'), 0),
                                          v.get('max_drctTxt'),
                                          formatter(v.get('srad'), 0),
                                          formatter(v.get('max_srad'), 0),
                                          v.get('online'))
            of.write(s.replace("'", ""))
        except:
            print kcci[sid]
            print sys.excepthook(sys.exc_info()[0],
                                 sys.exc_info()[1], sys.exc_info()[2])
            sys.exc_traceback = None

    of.close()
    subprocess.call(("/home/ldm/bin/pqinsert -p 'data c %s csv/kcci2.dat "
                     "bogus dat' %s") % (tstr, tmpfp), shell=True)
    os.remove(tmpfp)

    of = open(tmpfp, 'w')
    of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,")
    of.write("drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,")
    of.write("drct_max,max_sped,max_drctTxt,srad,max_srad,online\n")
    for sid in kimt.keys():
        v = kimt[sid]
        v['online'] = 1
        if (now - v['valid']).seconds > 3600:
            v['online'] = 0
        try:
            s = "%s,%s,%s,%s,%s," % (v.get('id'),
                                     v.get('ticks'),
                                     formatter(v.get('tmpf'), 0),
                                     formatter(v.get('dwpf'), 0),
                                     formatter(v.get('relh'), 0))
            s += "%s,%s,%s,%s," % (formatter(v.get('feel'), 0),
                                   formatter(v.get('pres'), 2),
                                   v.get('altiTend'), v.get('drctTxt'))
            s += "%s,%s,%s,%s," % (formatter(v.get('sped'), 0),
                                   formatter(v.get('sknt'), 0),
                                   formatter(v.get('drct'), 0),
                                   formatter(v.get('20gu'), 0))
            s += "%s,%s,%s,%s," % (formatter(v.get('gmph'), 0),
                                   v.get('gtim'),
                                   formatter(v.get('pday'), 2),
                                   formatter(v.get('pmonth'), 2))
            s += "%s,%s,%s," % (formatter(v.get('sknt'), 0),
                                formatter(v.get('drct'), 0),
                                formatter(v.get('20gu'), 0))
            s += "%s,%s,%s,%s,%s,%s\n" % (formatter(v.get('max_drct'), 0),
                                          formatter(v.get('max_sped'), 0),
                                          v.get('max_drctTxt'),
                                          formatter(v.get('srad'), 0),
                                          formatter(v.get('max_srad'), 0),
                                          v.get('online'))
            of.write(s.replace("'", ""))
        except:
            print kimt[sid]
            print sys.excepthook(sys.exc_info()[0],
                                 sys.exc_info()[1], sys.exc_info()[2])
            sys.exc_traceback = None

    of.close()
    cmd = ("/home/ldm/bin/pqinsert -p 'data c %s csv/kimt.dat "
           "bogus dat' %s") % (tstr, tmpfp)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    _ = p.stdout.read()
    os.remove(tmpfp)

    # Do KCCI stuff in WXC format
    of = open('/tmp/wxc_snet8.txt', 'w')
    of.write("""Weather Central 001d0300 Surface Data
  25
   5 Station
  52 CityName
  20 CityShort
   2 State
   7 Lat
   8 Lon
   2 Day
   4 Hour
   4 AirTemp
   4 AirDewp
   4 Feels Like
   4 Wind Direction Degrees
   4 Wind Direction Text
   4 Wind Speed
   4 Today Max Temp
   4 Today Min Temp
   4 Today Max Wind Gust MPH
   3 Today Max Wind Direction Text
   6 Today Precip
   6 Month Precip
   8 Time of Today Gust
   6 Last 2 Day Precip
   6 Last 3 Day Precip
   6 Last 7 Day Precip
   6 Last 14 Day Precip
""")

    for sid in kcci.keys():
        try:
            of.write("%5s %-52s %-20.20s %2s %7.2f %8.2f " % (
                sid, st.sts[sid]['plot_name'], st.sts[sid]['plot_name'], 'IA',
                st.sts[sid]['lat'], st.sts[sid]['lon']))
            of.write("%2s %4s %4.0f %4.0f %4.0f %4.0f %4s " % (
                kcci[sid]['valid'].day, kcci[sid]['valid'].hour,
                kcci[sid].get('tmpf') or -99,
                kcci[sid].get('dwpf') or -99,
                kcci[sid].get('feel') or -99, kcci[sid].get('drct') or -99,
                kcci[sid].get('drctTxt')))
            of.write("%4.0f %4.0f %4.0f %4.0f %3s " % (
                kcci[sid].get('sknt') or -99,
                kcci[sid].get('max_tmpf') or -99,
                kcci[sid].get('min_tmpf') or -99,
                kcci[sid].get('max_sped') or -99,
                kcci[sid].get('max_drctTxt')))
            of.write("%6.2f %6.2f %8s %6.2f %6.2f %6.2f %6.2f\n" % (
                kcci[sid]['pday'], kcci[sid]['pmonth'],
                kcci[sid].get('gtim2'), kcci[sid].get('p2day', 0),
                kcci[sid].get('p3day', 0), kcci[sid].get('p7day', 0),
                kcci[sid].get('p14day', 0)))

        except:
            print kcci[sid]
            print sys.excepthook(sys.exc_info()[0],
                                 sys.exc_info()[1], sys.exc_info()[2])
            sys.exc_traceback = None
    of.close()
    pqstr = 'data c 000000000000 wxc/wxc_snet8.txt bogus txt'
    subprocess.call(("/home/ldm/bin/pqinsert -p '%s' "
                     "/tmp/wxc_snet8.txt") % (pqstr, ), shell=True)
    os.remove("/tmp/wxc_snet8.txt")

if __name__ == '__main__':
    main()
