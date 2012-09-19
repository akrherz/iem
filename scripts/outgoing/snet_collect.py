"""
Collect up schoolnet data into files we have for outgoing...
"""

import mesonet
import sys
import time
import pickle
import os
import mx.DateTime
import network
import psycopg2.extras
import subprocess
import iemdb
import access
import tempfile

gmt = mx.DateTime.gmt()
tstr = gmt.strftime("%Y%m%d%H%M")

now = mx.DateTime.now()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

st = network.Table( ('KCCI','KELO','KIMT') )

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
        ob = d[sid].data
        ob["ticks"] = int(ob["ts"])
        if ob.get('tmpf') is not None and ob.get('dwpf') is not None:
            ob["relh"] = mesonet.relh(ob["tmpf"], ob["dwpf"])
        else:
            ob['relh'] = None
        if ob['relh'] == 'M':
            ob['relh'] = None
            
        if (ob.get('tmpf') is not None and ob.get('dwpf') is not None and
            ob.get('sped') is not None):
            ob["feel"] = mesonet.feelslike(ob["tmpf"], ob["relh"], ob["sped"])
        else:
            ob['feel'] = None
        if ob['feel'] == 'M':
            ob['feel'] = None
        ob["sped"] = ob["sknt"] * 1.17
        ob["altiTend"] = altiTxt(ob["alti_15m"])
        ob["drctTxt"] = mesonet.drct2dirTxt(ob["drct"])
        if ob["max_drct"] is None:
            ob["max_drct"] = 0
        ob["max_drctTxt"] = mesonet.drct2dirTxt(ob["max_drct"])
        ob["20gu"] = 0
        ob["gmph"] = ob["gust"] * 1.17
        ob["max_sped"] = ob["max_gust"] * 1.17
        ob["gtim"] = "0000"
        ob["gtim2"] = "12:00 AM"
        if ob["max_gust_ts"] is not None and ob["max_gust_ts"] != "null":
            ob["gtim"] = ob["max_gust_ts"].strftime("%H%M")
            ob["gtim2"] = ob["max_gust_ts"].strftime("%-I:%M %p")
        r[sid] = ob
    return r

def get_trend15(obs, network):
    icursor.execute("""SELECT s.id, t.* from trend_15m t JOIN stations s 
    on (s.iemid = t.iemid) WHERE network = '%s'""" % (
                                                network,) )
    for row in icursor:
        obs[ row["id"] ].data["alti_15m"] = row["alti_15m"]

def get_precip_totals(obs, network):
    now = mx.DateTime.now()
    for dy in (2,3,7,14):
        sql = """SELECT id, sum(pday) as rain from summary s JOIN stations t 
            ON (t.iemid = s.iemid) WHERE 
            network = '%s' and day > '%s' and pday >= 0 GROUP by id""" % (
                                                    network,
         (now - mx.DateTime.RelativeDateTime(days=dy)).strftime("%Y-%m-%d") )
        icursor.execute(sql)
        for row in icursor:
            obs[ row["id"]].data["p%sday" % (dy,)] = row["rain"]

def formatter(val, precision):
    if val is None or type(val) == type('s'):
        return 'M'
    fmt = '%%.%sf' % (precision,)
    return fmt % val

def main():
    kcci = access.get_network("KCCI", IEM)
    kelo = access.get_network("KELO", IEM)
    kimt = access.get_network("KIMT", IEM)
    
    get_trend15(kcci, 'KCCI')
    get_trend15(kelo, 'KELO')
    get_trend15(kimt, 'KIMT')
    get_precip_totals(kcci, 'KCCI')
    get_precip_totals(kelo, 'KELO')
    get_precip_totals(kimt, 'KIMT')
    computeOthers(kcci)
    computeOthers(kelo)
    computeOthers(kimt)

    tmpfp = tempfile.mktemp()
    of = open(tmpfp, 'w')
    of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,drct_max,max_sped,max_drctTxt,max_srad,\n")
    for sid in kcci.keys():
        v = kcci[sid].data
        try:
            s = "%s,%s,%s,%s,%s," % (v.get('id'),
                            v.get('ticks'), formatter(v.get('tmpf'),0), 
                            formatter(v.get('dwpf'),0),
                            formatter(v.get('relh'),0) )
            s += "%s,%s,%s,%s," % (
                        formatter(v.get('feel'), 0),
                        formatter(v.get('pres'), 2),
                        v.get('altiTend'), v.get('drctTxt'))
            s += "%s,%s,%s,%s," % (
                        formatter(v.get('sped'), 0),
                        formatter(v.get('sknt'), 0),
                        formatter(v.get('drct'), 0),
                        formatter(v.get('20gu'), 0))
            s += "%s,%s,%s,%s," % (
                        formatter(v.get('gmph'), 0),
                        v.get('gtim'),
                        formatter(v.get('pday'), 2),
                        formatter(v.get('pmonth'), 2))
            s += "%s,%s,%s," % (
                        formatter(v.get('sknt'), 0),
                        formatter(v.get('drct'), 0),
                        formatter(v.get('20gu'), 0))
            s += "%s,%s,%s,%s\n" % (
                        formatter(v.get('max_drct'), 0),
                        formatter(v.get('max_sped'), 0),
                        v.get('max_drctTxt'),
                        formatter(v.get('max_srad'), 0))
            of.write(s.replace("'", ""))
        except:
            print kcci[sid]
            print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
            sys.exc_traceback = None

    of.close()
    subprocess.call("/home/ldm/bin/pqinsert -p 'data c %s csv/kcci.dat bogus dat' %s" % (tstr, tmpfp), shell=True )
    os.remove(tmpfp)

    of = open(tmpfp, 'w')
    of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,")
    of.write("drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,")
    of.write("drct_max,max_sped,max_drctTxt,srad,max_srad,online,\n")
    for sid in kcci.keys():
        kcci[sid].data['online'] = 1
        if (now - kcci[sid].data['ts']) > 3600:
            kcci[sid].data['online'] = 0
        try:
            of.write(("%(id)s,%(ticks).0f,%(tmpf)s,%(dwpf)s," % kcci[sid].data ).replace("'", ""))
            of.write(("%(relh)s,%(feel)s,%(pres).2f,%(altiTend)s," % kcci[sid].data ).replace("'", "") )
            of.write(("%(drctTxt)s,%(sped).0f,%(sknt).0f,%(drct).0f," % kcci[sid].data ).replace("'", "") )
            of.write(("%(20gu).0f,%(gmph).0f,%(gtim)s,%(pday).2f," % kcci[sid].data  ).replace("'", ""))
            of.write(("%(pmonth).2f,%(min_tmpf).0f,%(max_tmpf).0f," % kcci[sid].data ).replace("'", "") )
            of.write(("%(max_sknt).0f,%(max_drct).0f,%(max_sped).0f," % kcci[sid].data ).replace("'", "") )
            of.write(("%(max_drctTxt)s,%(srad).0f,%(max_srad).0f,%(online)s,\n" % kcci[sid].data ).replace("'", "") )
        except:
            print kcci[sid].data
            print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
            sys.exc_traceback = None

    of.close()
    subprocess.call("/home/ldm/bin/pqinsert -p 'data c %s csv/kcci2.dat bogus dat' %s" % (
                                                                tstr, tmpfp), shell=True)
    os.remove(tmpfp)

    of = open(tmpfp, 'w')
    of.write("sid,ts,tmpf,dwpf,relh,feel,alti,altiTend,drctTxt,sped,sknt,")
    of.write("drct,20gu,gmph,gtim,pday,pmonth,tmpf_min,tmpf_max,max_sknt,")
    of.write("drct_max,max_sped,max_drctTxt,srad,max_srad,online\n")
    for sid in kimt.keys():
        if (now - kimt[sid].data['ts']) > 3600:
            kimt[sid].data['online'] = 0
  
        try:
            of.write(("%(id)s,%(ticks).0f,%(tmpf)s,%(dwpf)s," % kimt[sid].data ).replace("'", ""))
            of.write(("%(relh)s,%(feel)s,%(pres).2f,%(altiTend)s," % kimt[sid].data ).replace("'", "") )
            of.write(("%(drctTxt)s,%(sped).0f,%(sknt).0f,%(drct).0f," % kimt[sid].data ).replace("'", "") )
            of.write(("%(20gu).0f,%(gmph).0f,%(gtim)s,%(pday).2f," % kimt[sid].data  ).replace("'", ""))
            of.write(("%(pmonth).2f,%(min_tmpf).0f,%(max_tmpf).0f," % kimt[sid].data ).replace("'", "") )
            of.write(("%(max_sknt).0f,%(max_drct).0f,%(max_sped).0f," % kimt[sid].data ).replace("'", "") )
            of.write(("%(max_drctTxt)s,%(srad).0f,%(max_srad).0f,%(online)s,\n" % kimt[sid].data ).replace("'", "") )
  
        except:
            print kimt[sid].data
            print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
            sys.exc_traceback = None

    of.close()
    subprocess.call("/home/ldm/bin/pqinsert -p 'data c %s csv/kimt.dat bogus dat' %s"%(tstr, tmpfp), shell=True )
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
                kcci[sid].data['ts'].day, kcci[sid].data['ts'].hour, 
                kcci[sid].data.get('tmpf') or -99, kcci[sid].data.get('dwpf') or -99, 
                kcci[sid].data.get('feel') or -99, kcci[sid].data.get('drct'), 
                kcci[sid].data.get('drctTxt')))
            of.write("%4.0f %4.0f %4.0f %4.0f %3s " % (
                kcci[sid].data['sknt'], 
                kcci[sid].data['max_tmpf'], kcci[sid].data['min_tmpf'], 
                kcci[sid].data['max_sped'], kcci[sid].data.get('max_drctTxt')))
            of.write("%6.2f %6.2f %8s %6.2f %6.2f %6.2f %6.2f\n" % (
                kcci[sid].data['pday'], kcci[sid].data['pmonth'], 
                kcci[sid].data.get('gtim2'), kcci[sid].data.get('p2day',0), 
                kcci[sid].data.get('p3day',0), kcci[sid].data.get('p7day',0), 
                kcci[sid].data.get('p14day',0) ) )

        except:
            print kcci[sid].data
            print sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2] )
            sys.exc_traceback = None
    of.close()
    subprocess.call("/home/ldm/bin/pqinsert -p wxc_snet8.txt /tmp/wxc_snet8.txt",
                    shell=True)
    os.remove("/tmp/wxc_snet8.txt")

main()
