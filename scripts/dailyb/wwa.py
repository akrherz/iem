
import pg
import mx.DateTime

textfmt = """
             Summary +_________ By WFO ____________+  Watches 
Type         US   IA | ARX   DVN   DMX   OAX   FSD |  US 
Tornado     %(tu)3s  %(ti)3s | %(ta)3s   %(tv)3s   %(td)3s   %(to)3s   %(tf)3s | %(tw)3s
Svr Tstorm  %(su)3s  %(si)3s | %(sa)3s   %(sv)3s   %(sd)3s   %(so)3s   %(sf)3s | %(sw)3s
Fl Flood    %(fu)3s  %(fi)3s | %(fa)3s   %(fv)3s   %(fd)3s   %(fo)3s   %(ff)3s | N/A

ARX = LaCrosse, WI  DVN = Davenport, IA    DMX = Des Moines, IA 
OAX = Omaha, NE     FSD = Sioux Falls, SD

"""

htmlfmt = """
<table cellpadding="3" cellspacing="0" border="1">
<tr><td></td><th colspan="2">Summary</th><th colspan="5">By WFO</th><th>Watches</th></tr>
<tr><th>Type</th><th>US</th><th>IA</th><th>ARX</th><th>DVN</th><th>DMX</th><th>OAX</th><th>FSD</th><th>US</th></tr>
<tr><th>Tornado</th><td>%(tu)3s</td><td>%(ti)3s</td><td>%(ta)3s</td><td>%(tv)3s</td><td>%(td)3s</td><td>%(to)3s</td><td>%(tf)3s</td><td>%(tw)3s</td></tr>
<tr><th>Svr Tstorm</th><td>%(su)3s</td><td>%(si)3s</td><td>%(sa)3s</td><td>%(sv)3s</td><td>%(sd)3s</td><td>%(so)3s</td><td>%(sf)3s</td><td>%(sw)3s</td></tr>
<tr><th>Fl Flood</th><td>%(fu)3s</td><td>%(fi)3s</td><td>%(fa)3s</td><td>%(fv)3s</td><td>%(fd)3s</td><td>%(fo)3s</td><td>%(ff)3s</td><td>---</td></tr>
</table>

<p>ARX = LaCrosse, WI  DVN = Davenport, IA    DMX = Des Moines, IA 
OAX = Omaha, NE     FSD = Sioux Falls, SD

"""

def run():
    """ Generate listing of warning counts """
    mydb = pg.connect('postgis', 'iemdb', user='nobody')

    ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

    d = {}

    # Get US states
    d['tu'] = 0
    d['su'] = 0
    d['fu'] = 0
    rs = mydb.query("SELECT phenomena, count(*) as count from \
    (select distinct * from warnings_%s WHERE \
  gtype = 'P' and date(issue) = 'YESTERDAY' and phenomena IN ('TO','SV','FF')) as foo GROUP by phenomena" % (ts.year, ) ).dictresult()

    c = {'SV': 's', 'FF': 'f', 'TO': 't'}
    for i in range(len(rs)):
        d['%su' % (c[ rs[i]['phenomena'] ],)] = rs[i]['count']

    # Get Iowa
    d['ti'] = 0
    d['si'] = 0
    d['fi'] = 0
    sql = """
select phenomena, count(*) as count 
 from warnings_%s w, states s
WHERE contains(s.the_geom, w.geom) and s.state_name = 'Iowa' 
      and gtype = 'P' 
  and date(issue) = 'YESTERDAY' 
  and phenomena IN ('TO','SV','FF') GROUP by phenomena""" % (
     ts.year,) 
    rs = mydb.query(sql).dictresult()
    for i in range(len(rs)):
        d['%si' % (c[ rs[i]['phenomena'] ],)] = rs[i]['count']

    # Get per WFO
    f = {'DMX': 'd', 'DVN': 'v', 'ARX': 'a', 'FSD': 'f', 'OAX': 'o'}
    for key in f.keys():
        d['t%s' % (f[key],)] = 0
        d['s%s' % (f[key],)] = 0
        d['f%s' % (f[key],)] = 0
    sql = """
  SELECT phenomena, wfo, count(*) as count from warnings_%s WHERE 
  gtype = 'P' and date(issue) = 'YESTERDAY' 
  and phenomena IN ('TO','SV','FF') and
  wfo in ('DMX','FSD','ARX','DVN','OAX') GROUP by wfo, phenomena""" % (ts.year,)
    rs = mydb.query(sql).dictresult()
    for i in range(len(rs)):
        d['%s%s' % (c[ rs[i]['phenomena'] ], f[ rs[i]['wfo'] ])] = rs[i]['count']

    # SPC Watches
    d['tw'] = 0
    d['sw'] = 0

    c = {'SVR': 's', 'FFW': 'f', 'TOR': 't'}
    rs = mydb.query("SELECT type, count(*) as count from watches WHERE \
      date(issued) = 'YESTERDAY' GROUP by type").dictresult()
    for i in range(len(rs)):
        d['%sw' % (c[ rs[i]['type'] ],)] = rs[i]['count']


   
    txt = "> NWS Watch/Warning Summary for %s\n" % (ts.strftime("%d %b %Y"),)
    html = "<h3>NWS Watch/Warning Summary for %s</h3>" % (ts.strftime("%d %b %Y"),)

    txt += textfmt % d
    html += htmlfmt % d

    return txt, html
